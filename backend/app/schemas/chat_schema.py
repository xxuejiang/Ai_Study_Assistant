"""智能问答接口的数据模型。

Schema 层的作用类似 Java Web 里的 DTO/VO：
1. 规定前端请求必须传什么字段；
2. 规定后端响应会返回什么字段；
3. 自动生成 FastAPI 接口文档，便于接口调试。
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """智能问答请求体。"""

    message: str = Field(..., min_length=1, description="用户输入的问题")
    use_rag: bool = Field(default=False, description="是否启用资料问答。默认关闭，避免未上传资料时影响普通问答。")
    model: str | None = Field(default=None, description="模型名称，为空时使用后端默认模型")


class SourceItem(BaseModel):
    """资料来源片段。"""

    document_id: int
    filename: str
    chunk_index: int
    content: str


class ChatResponse(BaseModel):
    """智能问答响应体。"""

    id: int | None = Field(default=None, description="聊天记录 ID")
    answer: str
    sources: list[SourceItem] = []
    model: str
    use_rag: bool
    created_at: str | None = Field(default=None, description="记录创建时间")


class ChatHistoryItem(BaseModel):
    """聊天历史列表中的一条记录。"""

    id: int
    user_message: str
    assistant_answer: str
    use_rag: bool
    model: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """聊天历史响应体。"""

    items: list[ChatHistoryItem]
