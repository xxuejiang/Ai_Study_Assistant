"""智能问答业务服务。

Service 层负责业务流程编排，不直接写数据库 SQL，也不直接处理 HTTP 请求。
智能问答完整流程：
1. 接收用户问题；
2. 判断是否启用资料问答；
3. 如启用资料问答，则检索学习资料片段；
4. 构造 Prompt；
5. 调用大模型；
6. 保存聊天记录；
7. 返回给 API 层。
"""

from app.core.config import settings
from app.repositories.chat_repository import create_chat_message, list_recent_chat_messages
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.utils.prompt_templates import build_learning_assistant_prompt


class ChatService:
    """智能问答业务服务。"""

    def chat(self, message: str, use_rag: bool = False, model: str | None = None) -> dict:
        """处理一次聊天请求。

        设计说明：
        - use_rag=False：普通问答，直接调用模型；
        - use_rag=True：先尝试检索资料，再把资料片段放进 Prompt；
        - 如果用户勾选了资料问答，但资料库没有匹配内容，则自动降级为普通问答。

        自动降级很重要：
        用户未上传资料或问题与资料无关时，系统仍然应该可以正常回答，
        而不是因为没有资料就完全答不出来。
        """
        model_name = model or settings.DEFAULT_MODEL
        sources = []
        context = ""

        if use_rag:
            sources = rag_service.retrieve(message)
            context = rag_service.build_context(sources) if sources else ""

        # 只有真正检索到资料时，才使用“严格根据资料回答”的 Prompt。
        # 如果没有检索到资料，context 为空，Prompt 会自动切换为普通学习助手模式。
        messages = build_learning_assistant_prompt(message, context if context else None)
        answer = llm_service.chat(messages, model_name)

        # 每次问答都保存到数据库。刷新页面后，前端可以通过 /api/chat/history 重新加载。
        record_id = create_chat_message(message, answer, bool(context), model_name)

        return {
            "id": record_id,
            "answer": answer,
            "sources": [
                {
                    "document_id": s["document_id"],
                    "filename": s["filename"],
                    "chunk_index": s["chunk_index"],
                    "content": s["content"],
                }
                for s in sources
            ],
            "model": model_name,
            "use_rag": bool(context),
        }

    def history(self, limit: int = 30) -> dict:
        """查询聊天历史。"""
        items = list_recent_chat_messages(limit=limit)
        # SQLite 中 use_rag 保存为 0/1，这里转换成真正的 bool，前端处理更直观。
        for item in items:
            item["use_rag"] = bool(item["use_rag"])
        return {"items": items}


chat_service = ChatService()
