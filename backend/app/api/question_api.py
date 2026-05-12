"""练习题生成接口。"""

from fastapi import APIRouter, Query
from app.schemas.common_schema import MessageResponse
from app.schemas.question_schema import GenerationHistoryResponse, QuestionGenerateRequest, QuestionGenerateResponse
from app.services.generation_service import generation_service
from app.services.question_service import question_service

router = APIRouter()


@router.post("/questions/generate", response_model=QuestionGenerateResponse)
def generate_questions(request: QuestionGenerateRequest):
    """生成练习题，并保存生成历史。"""
    return question_service.generate(
        topic=request.topic,
        question_type=request.question_type,
        difficulty=request.difficulty,
        count=request.count,
        model=request.model,
        document_id=request.document_id,
    )


@router.get("/generations", response_model=GenerationHistoryResponse)
def list_generation_history(
    record_type: str | None = Query(default=None, description="question 或 summary；为空时返回全部生成记录"),
    limit: int = Query(default=50, ge=1, le=200),
):
    """查询题目生成/知识总结历史。"""
    return generation_service.list_history(record_type=record_type, limit=limit)


@router.delete("/generations/{record_id}", response_model=MessageResponse)
def delete_generation_record(record_id: int):
    """删除一条生成历史。"""
    return generation_service.delete(record_id)
