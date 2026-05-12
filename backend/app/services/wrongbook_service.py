"""错题本业务服务。"""
from fastapi import HTTPException
from app.repositories import wrongbook_repository

class WrongBookService:
    """错题本业务服务。"""
    def create(self, question: str, answer: str, explanation: str, difficulty: str) -> dict:
        """新增错题。"""
        qid = wrongbook_repository.create_wrong_question(question, answer, explanation, difficulty)
        return {'success': True, 'message': '错题已保存', 'id': qid}

    def list_all(self) -> dict:
        """查询全部错题。"""
        return {'items': wrongbook_repository.list_wrong_questions()}

    def update_status(self, question_id: int, status: str) -> dict:
        """修改错题状态。"""
        if not wrongbook_repository.update_wrong_question_status(question_id, status):
            raise HTTPException(status_code=404, detail='错题不存在。')
        return {'success': True, 'message': '错题状态已更新'}

    def delete(self, question_id: int) -> dict:
        """删除错题。"""
        if not wrongbook_repository.delete_wrong_question(question_id):
            raise HTTPException(status_code=404, detail='错题不存在。')
        return {'success': True, 'message': '错题已删除'}

wrongbook_service = WrongBookService()
