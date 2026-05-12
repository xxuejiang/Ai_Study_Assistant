"""知识总结接口。"""
from fastapi import APIRouter
from app.schemas.question_schema import SummaryRequest, SummaryResponse
from app.services.summary_service import summary_service

router = APIRouter()


@router.post("/summary", response_model=SummaryResponse)
def summarize(request: SummaryRequest):
    """生成知识点总结。"""
    return summary_service.summarize(
        topic=request.topic,
        use_rag=request.use_rag,
        model=request.model,
        document_id=request.document_id,
    )
