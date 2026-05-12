"""错题本接口。"""
from fastapi import APIRouter
from app.schemas.common_schema import MessageResponse
from app.schemas.wrongbook_schema import WrongQuestionCreateRequest, WrongQuestionStatusRequest, WrongQuestionListResponse
from app.services.wrongbook_service import wrongbook_service

router = APIRouter()

@router.get('/wrong-questions', response_model=WrongQuestionListResponse)
def list_wrong_questions():
    """查询错题列表。"""
    return wrongbook_service.list_all()

@router.post('/wrong-questions')
def create_wrong_question(request: WrongQuestionCreateRequest):
    """新增错题。"""
    return wrongbook_service.create(request.question, request.answer, request.explanation, request.difficulty)

@router.patch('/wrong-questions/{question_id}/status', response_model=MessageResponse)
def update_wrong_question_status(question_id: int, request: WrongQuestionStatusRequest):
    """修改错题状态。"""
    return wrongbook_service.update_status(question_id, request.status)

@router.delete('/wrong-questions/{question_id}', response_model=MessageResponse)
def delete_wrong_question(question_id: int):
    """删除错题。"""
    return wrongbook_service.delete(question_id)
