"""题目生成与知识总结接口的数据模型。

Schema 层用于约束前后端传输的数据格式。
本文件额外加入 document_id 字段，解决“题目生成默认应该基于已上传资料”的问题。
"""

from pydantic import BaseModel, Field
from app.schemas.chat_schema import SourceItem


class QuestionGenerateRequest(BaseModel):
    """题目生成请求体。

    document_id：
    - 为空：按知识点进行普通生成，同时尝试从全部资料中检索相关片段；
    - 不为空：优先围绕指定资料生成，适合实际使用中“先上传资料，再从资料出题”的流程。
    """

    topic: str = Field(..., min_length=1, description="知识点或主题")
    question_type: str = Field(default="选择题", description="题型：选择题、判断题、填空题、简答题")
    difficulty: str = Field(default="中等", description="难度：简单、中等、较难")
    count: int = Field(default=5, ge=1, le=20, description="题目数量")
    document_id: int | None = Field(default=None, description="可选：指定资料 ID")
    model: str | None = Field(default=None, description="模型名称")


class QuestionGenerateResponse(BaseModel):
    """题目生成响应体。"""

    id: int | None = Field(default=None, description="生成记录 ID")
    content: str
    sources: list[SourceItem] = []
    model: str
    document_id: int | None = None
    created_at: str | None = Field(default=None, description="记录创建时间")
    used_fallback: bool = Field(default=False, description="是否启用了后端格式兜底")


class SummaryRequest(BaseModel):
    """知识总结请求体。"""

    topic: str = Field(..., min_length=1, description="总结主题")
    use_rag: bool = Field(default=True, description="是否从资料中检索相关内容")
    document_id: int | None = Field(default=None, description="可选：指定资料 ID")
    model: str | None = Field(default=None, description="模型名称")


class SummaryResponse(BaseModel):
    """知识总结响应体。"""

    id: int | None = Field(default=None, description="生成记录 ID")
    summary: str
    sources: list[SourceItem] = []
    model: str
    document_id: int | None = None
    created_at: str | None = Field(default=None, description="记录创建时间")


class GenerationRecordItem(BaseModel):
    """AI 生成历史中的一条记录。"""

    id: int
    record_type: str
    topic: str
    question_type: str | None = None
    difficulty: str | None = None
    question_count: int | None = None
    document_id: int | None = None
    content: str
    model: str
    created_at: str


class GenerationHistoryResponse(BaseModel):
    """AI 生成历史响应体。"""

    items: list[GenerationRecordItem]
