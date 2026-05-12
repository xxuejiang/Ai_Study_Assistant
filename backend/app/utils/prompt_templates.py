"""Prompt 模板集中管理，方便集中维护和后续调整。"""


def build_learning_assistant_prompt(question: str, context: str | None = None) -> list[dict]:
    """构造学习助手问答 Prompt。"""
    system_prompt = (
        "你是一名认真负责的智能学习助手。回答要清晰、准确、适合用户理解。"
        "请使用规范 Markdown 格式输出，尽量使用标题、列表和分点说明。"
        "不要故意编造不存在的学习资料。"
    )

    if context:
        user_prompt = f"""
请严格根据下面提供的学习资料回答用户问题。
如果资料中没有相关内容，请明确说明“资料中没有找到相关依据”，不要编造。

【学习资料】
{context}

【用户问题】
{question}

请按以下 Markdown 结构回答：

## 一、简明回答

## 二、详细解释

## 三、资料依据

## 四、建议复习内容
"""
    else:
        user_prompt = f"""
【用户问题】
{question}

请按以下 Markdown 结构回答：

## 一、简明回答

## 二、详细解释

## 三、举例说明

## 四、建议复习内容
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt.strip()}]


def build_summary_prompt(topic: str, context: str | None = None) -> list[dict]:
    """构造知识总结 Prompt。"""
    system_prompt = (
        "你是一名学习资料整理助手，擅长把知识点整理成适合用户复习的结构化笔记。"
        "请使用规范 Markdown 格式输出。"
    )

    if context:
        user_prompt = f"""
请根据下面的学习资料，围绕“{topic}”整理知识点总结。

【学习资料】
{context}

请按以下 Markdown 结构输出：

## 一、核心概念

## 二、重点知识

## 三、容易混淆的地方

## 四、可能的考试题型

## 五、复习建议
"""
    else:
        user_prompt = f"""
请围绕“{topic}”整理一份适合用户复习的知识点总结。

请按以下 Markdown 结构输出：

## 一、核心概念

## 二、重点知识

## 三、容易混淆的地方

## 四、可能的考试题型

## 五、复习建议
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt.strip()}]


def _question_type_rule(question_type: str) -> str:
    """根据题型生成具体格式约束。"""
    if question_type == "选择题":
        return """
每道题必须包含一个明确题干，不能只列 A、B、C、D 四个陈述。
每道题必须包含 A、B、C、D 四个选项。
每道题只允许一个正确答案。
四个选项必须围绕同一个知识点设计。
正确选项应是资料要点的准确表述，但不要写“资料指出”“根据资料片段”。
错误选项要具体、合理，体现常见误解，例如概念混淆、范围扩大、条件缺失、因果倒置、片面概括。
禁止使用空泛模板选项，例如“与资料无关”“只能用于记忆”“以上都不符合”。
每道题必须包含：题目、A、B、C、D、答案、解析。
答案必须写成“答案：A”这种形式。
"""
    if question_type == "判断题":
        return """
每道题只能判断“正确”或“错误”。
每道题必须包含：题目、答案、解析。
不要生成 A、B、C、D 选项。
答案必须写成“答案：正确”或“答案：错误”。
"""
    if question_type == "填空题":
        return """
题干中必须使用“____”表示空缺位置。
每道题必须包含：题目、答案、解析。
不要生成 A、B、C、D 选项。
"""
    if question_type == "简答题":
        return """
题目应适合用户用 3-6 句话回答。
每道题必须包含：题目、参考答案、评分要点。
不要生成 A、B、C、D 选项。
"""
    return "每道题必须包含：题目、答案、解析。"


def build_question_prompt(topic: str, question_type: str, difficulty: str, count: int, context: str | None = None) -> list[dict]:
    """构造练习题生成 Prompt。

    输入给模型的不再是整段原始资料，而是后端筛选后的资料要点。
    这样可以降低小模型处理长文本和混乱格式时的跑偏概率。
    """
    system_prompt = (
        "你是一名练习题生成助手，擅长根据资料要点设计规范练习题。"
        "必须严格遵守题型、难度和数量要求。"
        "必须输出普通 Markdown 正文，不要使用代码围栏包裹整段内容。"
        "不要输出寒暄、解释任务过程或与题目无关的内容。"
    )
    material = f"【资料要点】\n{context}\n" if context else ""
    constraint = "题目必须优先基于上述资料要点，每道题尽量对应一个资料要点。" if context else "题目应围绕指定知识点生成。"
    type_rule = _question_type_rule(question_type)

    user_prompt = f"""
{material}
请围绕“{topic}”生成练习题。

【生成参数】
- 题型：{question_type}
- 数量：{count}
- 难度：{difficulty}

【必须遵守】
1. {constraint}
2. 必须生成 {count} 道题，不要多也不要少；
3. 每道题必须有独立题干，不能只列选项或只列知识点；
4. 每道题都必须有答案；
5. 每道题都必须有解析或评分要点；
6. 不要把整段内容放入代码块；
7. 不要使用表格；
8. 不要出现“资料指出”“根据资料片段”这类生硬表述；
9. 不要使用固定、重复、空泛的错误选项；
10. 严格按照下面的题型格式要求输出。

【题型格式要求】
{type_rule}

【标准输出模板】

## 第 1 题

**题目：** 这里写完整题干。

A. 选项 A
B. 选项 B
C. 选项 C
D. 选项 D

**答案：** A

**解析：** 这里写解析。
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt.strip()}]
