"""练习题输出校验与兜底格式化。

本模块处理本地小模型在题目生成中的常见问题：格式不稳定、选项重复、出现生硬模板。
处理思路保持轻量：优先使用模型输出；如果明显不合格，再根据后端筛选出的知识点生成稳定格式。
"""

from __future__ import annotations

import re
from app.utils.markdown_utils import normalize_markdown
from app.utils.text_utils import split_learning_units


OPTION_LABELS = ["A", "B", "C", "D"]
BAD_OPTION_PHRASES = [
    "该知识点与资料内容完全无关",
    "资料中的相关内容只能用于记忆",
    "以上说法都不符合资料内容",
    "资料指出",
    "根据资料片段",
]


def _plain_text(text: str | None) -> str:
    """把文本压缩成适合生成题目的普通文本。"""
    text = normalize_markdown(text or "")
    text = re.sub(r"【资料：[^】]+】", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _shorten(text: str, limit: int = 90) -> str:
    """截断过长文本，避免选项和解析过长。"""
    text = re.sub(r"\s+", " ", text or "").strip(" ：:，,、\t")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("，,；;、 ") + "……"


def _safe_count(count: int) -> int:
    """限制题目数量，防止本地设备生成太慢或页面过长。"""
    try:
        value = int(count)
    except Exception:
        value = 5
    return max(1, min(value, 20))


def _extract_facts(context: str | None, limit: int) -> list[str]:
    """从上下文中提取题目生成可用的知识点。"""
    text = _plain_text(context)
    if not text:
        return []
    facts = split_learning_units(text, max_units=max(limit * 3, 12))
    return facts[:limit]


def _extract_terms(text: str, topic: str) -> list[str]:
    """从文本中提取少量短语，用于构造更具体的干扰项。"""
    candidates: list[str] = []
    for pattern in [r"《([^》]{2,16})》", r"“([^”]{2,16})”", r"\"([^\"]{2,16})\"", r"[（(]([^）)]{2,16})[）)]"]:
        candidates.extend(re.findall(pattern, text))

    # 适度提取“xx的yy”“xx与yy”“xx是yy”等短语，避免只得到单字词。
    phrase_patterns = [
        r"([\u4e00-\u9fff]{2,10}的[\u4e00-\u9fff]{2,10})",
        r"([\u4e00-\u9fff]{2,10}与[\u4e00-\u9fff]{2,10})",
        r"([\u4e00-\u9fff]{2,10}是[\u4e00-\u9fff]{2,10})",
    ]
    for pattern in phrase_patterns:
        candidates.extend(re.findall(pattern, text))

    cleaned = re.sub(r"[，,。；;：:\s]+", "|", text)
    for part in cleaned.split("|"):
        part = part.strip("、-—()（）[]【】")
        if 2 <= len(part) <= 14:
            candidates.append(part)

    result: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        item = re.sub(r"\s+", "", item.strip())
        if not item or item.isdigit():
            continue
        if topic and item == topic:
            continue
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
        if len(result) >= 10:
            break
    return result


def _extract_key_concept(fact: str, topic: str) -> str:
    """从资料要点中提取一个较短的核心概念。"""
    fact = re.sub(r"\s+", " ", fact or "").strip()
    patterns = [
        r"([\u4e00-\u9fff]{2,12}(?:概念|定义|属性|特点|特征|作用|意义|原则|规律|阶段|关系|起源|发展))",
        r"((?:广义|狭义)[\u4e00-\u9fff]{2,8})",
        r"([\u4e00-\u9fff]{2,10}教育)",
    ]
    for pattern in patterns:
        match = re.search(pattern, fact)
        if match:
            return match.group(1)
    terms = _extract_terms(fact, topic)
    if terms:
        return terms[0]
    return topic or "该知识点"


def _collect_neighbor_concepts(facts: list[str], topic: str, exclude: str | None = None, limit: int = 6) -> list[str]:
    """从同批资料要点中提取相邻概念，用于构造更具体的干扰项。

    选择题质量差的一个常见原因是错误选项过于空泛，例如“只需机械背诵”。
    这里从同一份资料的其他要点中提取概念，让干扰项更像真实知识点之间的混淆，
    既能提升题目可读性，也不会引入额外模型调用或复杂算法。
    """
    result: list[str] = []
    seen: set[str] = set()
    exclude = (exclude or "").strip()
    for fact in facts:
        concept = _extract_key_concept(fact, topic).strip()
        concept = re.sub(r"^[：:，,。；;、\s]+|[：:，,。；;、\s]+$", "", concept)
        if not concept or concept == topic or concept == exclude:
            continue
        if len(concept) < 2 or len(concept) > 24:
            continue
        if concept in seen:
            continue
        seen.add(concept)
        result.append(concept)
        if len(result) >= limit:
            break
    return result


def _pick_concept_terms(fact: str, topic: str, max_terms: int = 3) -> list[str]:
    """从单个资料要点中抽取少量可读术语。

    该函数服务于兜底题目生成。它不追求中文分词的精确性，只保留适合放到选项里的
    短语，过滤掉过短、过长、过于口语化或纯编号内容。
    """
    raw_terms = _extract_terms(fact, topic)
    terms: list[str] = []
    seen: set[str] = set()
    bad_words = {"资料", "内容", "相关", "理解", "问题", "需要", "关于", "下列", "说法"}
    for item in raw_terms:
        item = re.sub(r"\s+", "", item.strip("：:，,。；;、()（）[]【】"))
        if not item or item in seen or item in bad_words:
            continue
        if item == topic or item.isdigit():
            continue
        if len(item) < 2 or len(item) > 18:
            continue
        seen.add(item)
        terms.append(item)
        if len(terms) >= max_terms:
            break
    return terms


def _build_correct_option(topic: str, fact: str) -> str:
    """根据资料要点生成正确选项。

    正确选项尽量避免直接照抄整段资料，也避免“资料指出”这种生硬表达。
    处理方式是先识别核心概念，再根据“阶段、属性、概念、关系、作用”等常见知识类型
    做轻量改写。这样生成的选项比纯模板更自然，也方便后续讲解。
    """
    topic = topic or "该知识点"
    fact = re.sub(r"\s+", " ", fact or "").strip()
    concept = _extract_key_concept(fact, topic)
    terms = _pick_concept_terms(fact, topic, max_terms=3)
    term_text = "、".join(terms[:2]) if terms else concept

    if re.search(r"(阶段|发展|演变|形成)", concept):
        if re.search(r"(独立|多样|多元|流派)", concept + fact):
            return f"{concept}强调{topic}逐步形成相对独立的研究领域，并呈现不同理论取向和发展形态。"
        return f"{concept}强调{topic}在不同历史条件下的演变过程和阶段性特征。"

    if re.search(r"(概念|定义|内涵|外延)", concept + fact):
        return f"理解{concept}时，应同时关注其基本含义、适用范围以及资料中的限定条件。"

    if re.search(r"(属性|特点|特征)", concept + fact):
        return f"{concept}需要从资料中的多个维度综合理解，不能只抓住其中某一个方面。"

    if re.search(r"(关系|与)", concept + fact):
        return f"{concept}强调相关因素之间存在相互影响或相互制约，不能割裂开来理解。"

    if re.search(r"(作用|意义|价值|功能)", concept + fact):
        return f"{concept}体现了{topic}在实际理解和分析问题中的作用，需要结合具体语境把握。"

    if re.search(r"(包括|包含|分为|主要有|表现为)", fact):
        return f"{concept}应结合资料中列举的{term_text}等内容进行整体把握。"

    statement = _shorten(fact, 88)
    statement = re.sub(r"^(资料指出|根据资料|资料片段)[:：]?", "", statement).strip()
    if len(statement) <= 20:
        return f"{concept}是理解“{topic}”时需要关注的具体知识点。"
    return statement


def _make_statement(fact: str, topic: str) -> str:
    """把资料事实整理成适合放入正确选项的表述。"""
    return _build_correct_option(topic, fact)

def _build_choice_distractors(topic: str, fact: str, all_facts: list[str], index: int) -> list[str]:
    """生成选择题干扰项。

    v14 调整重点：干扰项尽量围绕同一资料中的真实概念展开，而不是使用固定套话。
    这样题目仍然是轻量规则生成，学生容易理解；同时比“机械背诵、与资料无关”这类
    模板选项更接近正常试题。
    """
    topic = topic or "该知识点"
    concept = _extract_key_concept(fact, topic)
    neighbor_concepts = _collect_neighbor_concepts(all_facts, topic, exclude=concept, limit=6)
    terms = _pick_concept_terms(" ".join([fact, *all_facts]), topic, max_terms=5)

    wrong_1 = neighbor_concepts[0] if len(neighbor_concepts) >= 1 else (terms[0] if terms else "其他知识点")
    wrong_2 = neighbor_concepts[1] if len(neighbor_concepts) >= 2 else (terms[1] if len(terms) >= 2 else "某一局部内容")
    wrong_3 = neighbor_concepts[2] if len(neighbor_concepts) >= 3 else (terms[2] if len(terms) >= 3 else "单一条件")

    if re.search(r"(阶段|发展|演变|形成)", concept + fact):
        templates = [
            f"把{concept}简单理解为单一时间顺序，忽视其背后的学科形成、理论变化或社会条件。",
            f"将{concept}直接等同于{wrong_1}，混淆了不同知识点的考查对象。",
            f"认为{concept}只说明某个历史节点，不涉及资料中呈现的连续发展过程。",
            f"把{wrong_2}当成{concept}的全部内容，缩小了该知识点的理解范围。",
        ]
    elif re.search(r"(概念|定义|内涵|外延)", concept + fact):
        templates = [
            f"把{concept}只理解为一个词语解释，忽视其适用范围和限定条件。",
            f"将{concept}与{wrong_1}混为一谈，导致核心含义发生偏移。",
            f"认为{concept}只需要记住表述，不需要结合具体语境进行判断。",
            f"把{wrong_2}当成{concept}的完整定义，存在以偏概全的问题。",
        ]
    elif re.search(r"(属性|特点|特征)", concept + fact):
        templates = [
            f"只强调{concept}中的某一个方面，忽视资料中体现的其他属性或特征。",
            f"将{concept}与{wrong_1}直接等同，混淆了属性判断和概念分类。",
            f"把{wrong_2}当成{concept}的唯一表现，缩小了知识点范围。",
            f"认为{concept}可以脱离对象和条件单独判断，忽视资料语境。",
        ]
    elif re.search(r"(关系|与)", concept + fact):
        templates = [
            f"把{concept}理解为单向决定关系，忽视相关因素之间可能存在的相互影响。",
            f"将{concept}与{wrong_1}混同，导致分析对象发生变化。",
            f"只看到{wrong_2}这一局部因素，忽视关系判断中的条件和范围。",
            f"认为{concept}可以不结合资料语境直接下结论，分析过于绝对。",
        ]
    elif re.search(r"(作用|意义|价值|功能)", concept + fact):
        templates = [
            f"把{concept}理解为抽象口号，没有说明其在问题分析中的具体作用。",
            f"将{concept}与{wrong_1}混淆，忽视二者在资料中的不同指向。",
            f"只强调{wrong_2}，没有体现{concept}的完整作用范围。",
            f"认为{concept}没有实际分析价值，只是形式化表述。",
        ]
    else:
        templates = [
            f"将{concept}直接等同于{wrong_1}，混淆了资料中的不同知识点。",
            f"只抓住{wrong_2}这一局部表述，忽视{concept}的完整含义。",
            f"把{wrong_3}作为{concept}的唯一条件，表述过于绝对。",
            f"扩大{concept}的适用范围，把局部材料当作普遍结论。",
        ]

    distractors: list[str] = []
    start = (index - 1) % len(templates)
    for offset in range(len(templates)):
        item = templates[(start + offset) % len(templates)]
        item = _shorten(item, 96)
        if item not in distractors and item != fact:
            distractors.append(item)
        if len(distractors) == 3:
            break
    return distractors

def _split_options_from_content(text: str) -> list[str]:
    """提取模型输出中的选项文本，用于检测重复和模板化问题。"""
    options = re.findall(r"(?:^|\n)\s*[A-D][\.、．]\s*(.+)", text)
    return [re.sub(r"\s+", " ", item).strip() for item in options]


def validate_question_content(content: str, question_type: str, count: int) -> bool:
    """检查模型输出是否满足基本展示要求。"""
    text = normalize_markdown(content)
    if not text or len(text) < 20:
        return False

    if text.strip().startswith("```"):
        return False

    expected_count = _safe_count(count)
    question_headers = re.findall(r"第\s*\d+\s*题", text)
    if len(question_headers) < expected_count:
        return False

    if "题目" not in text or "答案" not in text:
        return False

    if question_type in {"选择题", "判断题", "填空题"} and "解析" not in text:
        return False

    if any(phrase in text for phrase in BAD_OPTION_PHRASES):
        return False

    if question_type == "选择题":
        has_a = re.search(r"(^|\n)\s*A[\.、．]\s*", text) is not None
        has_b = re.search(r"(^|\n)\s*B[\.、．]\s*", text) is not None
        has_c = re.search(r"(^|\n)\s*C[\.、．]\s*", text) is not None
        has_d = re.search(r"(^|\n)\s*D[\.、．]\s*", text) is not None
        if not (has_a and has_b and has_c and has_d):
            return False

        options = _split_options_from_content(text)
        if len(options) < expected_count * 4:
            return False
        unique_options = set(options)
        if len(unique_options) < max(4, int(len(options) * 0.65)):
            return False
        long_option_count = sum(1 for item in options if len(item) > 120)
        if long_option_count > expected_count:
            return False
        return True

    if question_type == "判断题":
        return "正确" in text or "错误" in text

    if question_type == "填空题":
        return "____" in text or "______" in text

    if question_type == "简答题":
        return "参考答案" in text or "评分要点" in text

    return True


def _append_choice_question(lines: list[str], index: int, topic: str, fact: str, facts: list[str]) -> None:
    """向 Markdown 行列表中追加一道选择题。

    题干围绕具体概念，而不是笼统围绕“主题”。正确选项使用资料要点的改写表达，
    错误选项围绕相邻概念或常见误解构造，避免所有题都长成同一种模板。
    """
    concept = _extract_key_concept(fact, topic)
    correct_option = _make_statement(fact, topic)
    distractors = _build_choice_distractors(topic, fact, facts, index)

    answer_position = (index - 1) % 4
    options = distractors[:]
    options.insert(answer_position, correct_option)
    answer_label = OPTION_LABELS[answer_position]

    lines.extend([
        f"## 第 {index} 题",
        "",
        f"**题目：** 关于“{concept}”，下列理解最准确的是哪一项？",
        "",
    ])

    for label, option in zip(OPTION_LABELS, options):
        lines.append(f"{label}. {option}")

    lines.extend([
        "",
        f"**答案：** {answer_label}",
        "",
        f"**解析：** 本题考查“{concept}”。选项 {answer_label} 保留了该知识点的核心含义和限定条件；其余选项主要存在概念混淆、范围缩小或扩大、绝对化表述等问题。",
        "",
    ])

def build_fallback_questions(
    topic: str,
    question_type: str,
    difficulty: str,
    count: int,
    context: str | None = None,
    knowledge_units: list[str] | None = None,
) -> str:
    """生成格式稳定的兜底题目。"""
    total = _safe_count(count)
    topic = (topic or "资料内容").strip()
    difficulty = (difficulty or "中等").strip()
    facts = [item for item in (knowledge_units or []) if item]
    if len(facts) < total:
        for fact in _extract_facts(context, total * 2):
            if fact not in facts:
                facts.append(fact)
            if len(facts) >= total:
                break

    if not facts:
        facts = [f"{topic}是本次需要重点理解的内容"]

    lines = [
        f"# 练习题：{topic}",
        "",
        f"> 题型：{question_type}｜难度：{difficulty}｜数量：{total}",
        "",
    ]

    for index in range(1, total + 1):
        fact = facts[(index - 1) % len(facts)]
        short_fact = _shorten(fact, 80)

        if question_type == "选择题":
            _append_choice_question(lines, index, topic, fact, facts)
        elif question_type == "判断题":
            is_true = index % 2 == 1
            statement = _make_statement(fact, topic) if is_true else f"{topic}可以脱离资料中的条件、对象和语境直接下结论。"
            answer = "正确" if is_true else "错误"
            lines.extend([
                f"## 第 {index} 题",
                "",
                f"**题目：** {statement}",
                "",
                f"**答案：** {answer}",
                "",
                f"**解析：** 相关资料要点为：“{short_fact}”。判断时需要关注表述是否准确、是否保留限定条件。",
                "",
            ])
        elif question_type == "填空题":
            lines.extend([
                f"## 第 {index} 题",
                "",
                f"**题目：** 根据资料要点，补全与“{topic}”相关的关键表述：____。",
                "",
                f"**答案：** {short_fact}",
                "",
                "**解析：** 该空考查对资料关键信息的提取和概括能力。",
                "",
            ])
        else:
            lines.extend([
                f"## 第 {index} 题",
                "",
                f"**题目：** 请结合资料，简要说明“{topic}”相关内容。",
                "",
                f"**参考答案：** 可以围绕“{short_fact}”展开，说明其核心含义、限定条件以及与具体问题的关系。",
                "",
                "**评分要点：**",
                "- 能准确概括资料要点；",
                "- 能说明核心含义和限定条件；",
                "- 能结合具体语境进行分析；",
                "- 表达清楚，逻辑完整。",
                "",
            ])

    return "\n".join(line for line in lines if line is not None).strip()


def normalize_or_fallback_question_content(
    raw_content: str,
    topic: str,
    question_type: str,
    difficulty: str,
    count: int,
    context: str | None = None,
    knowledge_units: list[str] | None = None,
) -> tuple[str, bool]:
    """清洗并校验模型输出，不合格时返回兜底题目。"""
    cleaned = normalize_markdown(raw_content)
    if validate_question_content(cleaned, question_type, count):
        return cleaned, False
    return build_fallback_questions(topic, question_type, difficulty, count, context, knowledge_units), True
