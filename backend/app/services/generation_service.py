"""AI 生成历史业务服务。"""

from fastapi import HTTPException
from app.repositories import generation_repository


class GenerationService:
    """统一管理题目生成、知识总结等 AI 生成历史。"""

    def list_history(self, record_type: str | None = None, limit: int = 50) -> dict:
        """查询生成历史。"""
        return {"items": generation_repository.list_generation_records(record_type=record_type, limit=limit)}

    def delete(self, record_id: int) -> dict:
        """删除生成历史。"""
        if not generation_repository.delete_generation_record(record_id):
            raise HTTPException(status_code=404, detail="生成记录不存在。")
        return {"success": True, "message": "生成记录已删除"}


generation_service = GenerationService()
