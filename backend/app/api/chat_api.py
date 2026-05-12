"""智能问答接口。

API 层相当于 Java Web 中的 Controller：
- 接收前端请求；
- 调用 Service 层；
- 把结果返回给前端；
- 不直接写复杂业务逻辑。
"""

from fastapi import APIRouter, Query
from app.schemas.common_schema import MessageResponse
from app.schemas.chat_schema import ChatHistoryResponse, ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.repositories.chat_repository import delete_chat_message, clear_chat_messages

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """AI 问答接口。"""
    return chat_service.chat(message=request.message, use_rag=request.use_rag, model=request.model)


@router.get("/chat/history", response_model=ChatHistoryResponse)
def list_chat_history(limit: int = Query(default=30, ge=1, le=200)):
    """查询聊天历史。

    前端刷新后会调用该接口，把数据库中的历史问答重新显示出来。
    """
    return chat_service.history(limit=limit)


@router.delete("/chat/history/{message_id}", response_model=MessageResponse)
def delete_history_item(message_id: int):
    """删除单条聊天历史。"""
    ok = delete_chat_message(message_id)
    return {"success": ok, "message": "聊天记录已删除" if ok else "聊天记录不存在"}


@router.delete("/chat/history", response_model=MessageResponse)
def clear_history():
    """清空聊天历史。"""
    count = clear_chat_messages()
    return {"success": True, "message": f"已清空 {count} 条聊天记录"}
