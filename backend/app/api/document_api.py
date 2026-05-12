"""资料管理接口。"""
from fastapi import APIRouter, UploadFile, File
from app.schemas.common_schema import MessageResponse
from app.schemas.document_schema import DocumentListResponse, DocumentUploadResponse, DocumentChunkListResponse
from app.services.document_service import document_service

router = APIRouter()

@router.post('/documents/upload', response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传学习资料，并自动解析、清洗、切分、保存。"""
    return await document_service.upload_document(file)

@router.get('/documents', response_model=DocumentListResponse)
def list_documents():
    """查询已上传资料列表。"""
    return document_service.list_documents()

@router.get('/documents/{document_id}/chunks', response_model=DocumentChunkListResponse)
def list_document_chunks(document_id: int):
    """查看指定资料切分后的文本片段。"""
    return document_service.list_chunks(document_id)

@router.delete('/documents/{document_id}', response_model=MessageResponse)
def delete_document(document_id: int):
    """删除资料及其片段。"""
    return document_service.delete_document(document_id)
