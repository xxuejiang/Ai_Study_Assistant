"""系统状态相关接口。"""

from fastapi import APIRouter

from app.core.config import settings
from app.repositories.chat_repository import count_chat_messages
from app.repositories.document_repository import list_documents
from app.repositories.generation_repository import count_generation_records
from app.repositories.wrongbook_repository import count_wrong_questions
from app.services.ollama_service import ollama_service

router = APIRouter()


@router.get("/health")
def health_check():
    """后端健康检查。前端可以用它判断 FastAPI 是否正常启动。"""
    return {"status": "ok", "message": "AI Study Assistant backend is running."}


@router.get("/model/status")
def model_status():
    """检查 Ollama 服务是否可访问。"""
    available = ollama_service.is_available()
    return {
        "available": available,
        "base_url": settings.OLLAMA_BASE_URL,
        "api_base_url": settings.OLLAMA_API_BASE_URL,
        "default_model": settings.DEFAULT_MODEL,
        "message": "Ollama service is available." if available else "Ollama service is not available.",
    }


@router.get("/dashboard")
def dashboard():
    """首页仪表盘数据。"""
    installed_models = ollama_service.list_models()
    return {
        "document_count": len(list_documents()),
        "wrong_question_count": count_wrong_questions(),
        "chat_count": count_chat_messages(),
        "generation_count": count_generation_records(),
        "default_model": settings.DEFAULT_MODEL,
        "ollama_available": ollama_service.is_available(),
        "installed_model_count": len(installed_models),
    }


@router.get("/models")
def list_models():
    """返回页面可选择的大模型列表。

    installed_models 来自 Ollama 本机；recommended_models 来自 project.config.json。
    推荐模型只用于下拉展示，不代表本机一定已经安装。
    """
    installed_models = ollama_service.list_models()
    installed_set = set(installed_models)
    recommended_models = settings.RECOMMENDED_MODELS

    option_names: list[str] = []
    for name in installed_models + recommended_models:
        if name not in option_names:
            option_names.append(name)

    return {
        "available": ollama_service.is_available(),
        "base_url": settings.OLLAMA_BASE_URL,
        "api_base_url": settings.OLLAMA_API_BASE_URL,
        "default_model": settings.DEFAULT_MODEL,
        "installed_models": installed_models,
        "recommended_models": recommended_models,
        "options": [
            {
                "name": name,
                "installed": name in installed_set,
                "label": f"{name}{'（已安装）' if name in installed_set else '（推荐，需先下载）'}",
            }
            for name in option_names
        ],
    }
