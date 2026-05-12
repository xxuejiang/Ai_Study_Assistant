"""资料管理接口的数据模型。"""
from pydantic import BaseModel

class DocumentItem(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    chunk_count: int
    created_at: str

class DocumentListResponse(BaseModel):
    items: list[DocumentItem]

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    chunk_count: int
    message: str

class DocumentChunkItem(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str

class DocumentChunkListResponse(BaseModel):
    items: list[DocumentChunkItem]
