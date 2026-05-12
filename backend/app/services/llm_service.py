"""统一大模型调用服务。业务层通过这里调用模型，避免直接依赖 Ollama。"""
from app.core.config import settings
from app.services.ollama_service import ollama_service

class LLMService:
    """大模型服务统一入口。"""
    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        """当前版本默认调用 Ollama。后续可以在这里扩展云端 API。"""
        return ollama_service.chat(messages=messages, model=model or settings.DEFAULT_MODEL)

llm_service = LLMService()
