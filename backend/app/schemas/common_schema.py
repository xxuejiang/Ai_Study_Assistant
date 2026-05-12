"""通用响应模型。"""
from pydantic import BaseModel

class MessageResponse(BaseModel):
    """简单消息响应。"""
    success: bool = True
    message: str
