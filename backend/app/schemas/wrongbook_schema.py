"""错题本接口的数据模型。"""
from pydantic import BaseModel, Field

class WrongQuestionCreateRequest(BaseModel):
    question: str = Field(..., min_length=1, description="题目内容")
    answer: str = Field(..., min_length=1, description="正确答案")
    explanation: str = Field(default="", description="答案解析")
    difficulty: str = Field(default="中等", description="难度")

class WrongQuestionStatusRequest(BaseModel):
    status: str = Field(..., description="错题状态，如：未掌握、已掌握")

class WrongQuestionItem(BaseModel):
    id: int
    question: str
    answer: str
    explanation: str | None = ""
    difficulty: str | None = ""
    status: str
    created_at: str

class WrongQuestionListResponse(BaseModel):
    items: list[WrongQuestionItem]
