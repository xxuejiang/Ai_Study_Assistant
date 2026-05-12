"""Markdown 文本清洗工具。

大模型经常会把整段回答包在 ```markdown ... ``` 代码块里。
这种格式在聊天软件里看着没问题，但前端 Markdown 渲染器会把它当成“代码块”，
导致整块内容变成黑底等宽字体，不适合展示给用户。

因此后端在保存和返回结果前，先做一次轻量清洗：
1. 去掉最外层的 markdown/code 代码围栏；
2. 去掉明显多余的首尾空白；
3. 尽量不改动正文内容，避免破坏模型输出。
"""

from __future__ import annotations

import re


def strip_outer_code_fence(content: str | None) -> str:
    """移除包裹整段内容的 Markdown 代码围栏。

    示例：
    ```markdown
    ## 第 1 题
    ...
    ```

    会被转换为：
    ## 第 1 题
    ...

    说明：
    这里只处理“整段内容被一个代码块包住”的情况。
    如果正文中间真的包含代码块，不会被误删。
    """
    text = (content or "").strip()
    if not text:
        return ""

    pattern = re.compile(r"^```(?:markdown|md|text|json)?\s*\n(?P<body>[\s\S]*?)\n```\s*$", re.IGNORECASE)
    match = pattern.match(text)
    if match:
        return match.group("body").strip()

    return text


def normalize_markdown(content: str | None) -> str:
    """统一入口：对大模型返回的 Markdown 做基础清洗。"""
    return strip_outer_code_fence(content)
