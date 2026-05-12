"""文本清洗、切分、关键词检索与生成材料整理工具。"""

from __future__ import annotations

import re
from app.core.config import settings


def clean_text(text: str) -> str:
    """基础文本清洗。

    这里只处理通用且低风险的噪声：换行、空格、连续空行等。
    不在这里强行删除“1.”、“答案”、“解析”等内容，避免误删不同格式资料中的有效信息。
    """
    text = text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\u3000]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text_for_generation(text: str) -> str:
    """面向 AI 生成任务的保守清洗。

    该函数只处理明显无意义、跨资料格式也较稳定的噪声，例如页码、分隔线、代码围栏。
    对题号、括号序号、答案、解析等内容不做简单粗暴删除，原因是这些内容在某些资料中
    可能本身就是知识结构的一部分。真正提升生成质量的关键不只是清洗，而是后续的片段筛选。
    """
    text = clean_text(text)
    if not text:
        return ""

    # 去掉 Markdown 代码围栏，防止后续模型把整段当成代码块处理。
    text = text.replace("```markdown", "").replace("```text", "").replace("```", "")

    # 去掉常见页码和长分隔线。该类信息通常不承载知识内容。
    text = re.sub(r"(?m)^\s*第\s*\d+\s*页\s*$", "", text)
    text = re.sub(r"(?m)^\s*[-_=—]{5,}\s*$", "", text)

    # 统一一些容易干扰切分的全角符号。
    text = text.replace("【", " 【").replace("】", "】 ")
    text = re.sub(r"[ \t\u3000]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """把长文本切成多个片段。片段是后续资料检索的基础单位。"""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    text = clean_text(text)
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def extract_terms(question: str) -> list[str]:
    """从问题中提取简单关键词。为降低依赖，不引入额外中文分词库。"""
    question = (question or "").strip().lower()
    terms = set()
    for token in re.findall(r"[a-zA-Z0-9_]+", question):
        if len(token) >= 2:
            terms.add(token)
    for block in re.findall(r"[\u4e00-\u9fff]+", question):
        if len(block) >= 2:
            terms.add(block)
        for i in range(len(block) - 1):
            terms.add(block[i:i+2])
        for i in range(len(block) - 2):
            terms.add(block[i:i+3])
    stop_terms = {"什么", "怎么", "如何", "为什么", "一个", "这个", "那个", "请问", "根据", "资料", "内容"}
    return [x for x in terms if x not in stop_terms]


def score_chunk(question: str, chunk: str) -> int:
    """计算问题与资料片段的相关性分数。基础版检索使用该分数排序。"""
    score = 0
    chunk_lower = (chunk or "").lower()
    for term in extract_terms(question):
        if term.lower() in chunk_lower:
            score += len(term)
    return score


def _remove_inline_noise(text: str) -> str:
    """清理单个候选知识点内部的轻量噪声。"""
    text = re.sub(r"\s+", " ", text or "").strip()
    text = text.strip(" ：:，,。.;；、-—")

    # 去掉孤立的题型标签，但不删除后面的知识内容。
    text = re.sub(r"^【\s*(单选|多选|判断|辨析|简答|填空|答案|解析)\s*】\s*[:：]?\s*", "", text)
    text = re.sub(r"^(答案|解析)\s*[:：]\s*", "", text)

    # 去掉开头序号，保留主体内容。
    text = re.sub(r"^\s*(\d+|[一二三四五六七八九十]+)[\.、]\s*", "", text)
    text = re.sub(r"^\s*[（(](\d+|[一二三四五六七八九十]+)[）)]\s*", "", text)
    return text.strip()


def split_learning_units(text: str, max_units: int = 80) -> list[str]:
    """从资料中切出适合生成题目的候选知识点。

    切分策略保持轻量：按换行、句号、分号、题型标签和序号边界切分，随后过滤过短、过长、
    明显不是知识表达的片段。这样比直接把整段资料交给模型更稳定，也不依赖固定文件格式。
    """
    text = clean_text_for_generation(text)
    if not text:
        return []

    split_pattern = r"[。；;\n]+|(?=【\s*(单选|多选|判断|辨析|简答|填空)\s*】)|(?=\d+[\.、])|(?=[（(]\d+[）)])"
    raw_parts = re.split(split_pattern, text)

    units: list[str] = []
    seen: set[str] = set()
    for part in raw_parts:
        if not part:
            continue
        item = _remove_inline_noise(str(part))
        if len(item) < 8:
            continue
        if len(item) > 160:
            item = item[:160].rstrip("，,；;、 ") + "……"

        # 过滤明显不适合出题的残留内容。
        if re.fullmatch(r"[A-Da-d][\.、．]?", item):
            continue
        if item in {"单选", "多选", "判断", "辨析", "简答", "填空", "答案", "解析"}:
            continue

        # 过滤类似“1人1书1教育 2教育定义”这种从题库选项中挤压出来的残片。
        # 这种内容通常不是完整知识表述，直接用于出题会导致题目质量很差。
        if len(re.findall(r"\d[\u4e00-\u9fff]", item)) >= 2 and "。" not in item:
            continue

        key = re.sub(r"\W+", "", item)
        if not key or key in seen:
            continue
        seen.add(key)
        units.append(item)
        if len(units) >= max_units:
            break
    return units


def select_learning_units_for_topic(text: str, topic: str, count: int) -> list[str]:
    """根据主题从候选知识点中选择最适合生成题目的片段。

    选择逻辑尽量简单：先用已有关键词评分排序，命中主题的片段优先；如果命中不足，补充靠前的
    候选片段。这样可以兼顾“围绕主题”和“资料格式不确定”两种情况。
    """
    target = max(1, min(int(count or 5), 20))
    units = split_learning_units(text, max_units=max(target * 6, 30))
    if not units:
        return []

    scored: list[tuple[int, int, str]] = []
    for index, unit in enumerate(units):
        score = score_chunk(topic, unit)
        if topic and topic in unit:
            score += 20
        # 定义、特点、作用、原因、关系等词通常更适合出题。
        if re.search(r"(定义|概念|特点|特征|作用|意义|原因|关系|原则|规律|阶段|属性|类型|方法)", unit):
            score += 6
        scored.append((score, -index, unit))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    selected = [unit for score, _, unit in scored if score > 0][:target]

    if len(selected) < target:
        for unit in units:
            if unit not in selected:
                selected.append(unit)
            if len(selected) >= target:
                break

    return selected[:target]


def build_generation_material(text: str, topic: str, count: int) -> tuple[str, list[str]]:
    """为题目生成构造更干净的资料输入。

    返回值：
    - material：传给模型的资料要点文本；
    - units：本次选中的知识点列表，供兜底格式化使用。
    """
    units = select_learning_units_for_topic(text, topic, count)
    if not units:
        material = clean_text_for_generation(text)
        return material[: settings.MAX_CONTEXT_CHARS], []

    lines = [f"{i}. {unit}" for i, unit in enumerate(units, start=1)]
    return "\n".join(lines), units
