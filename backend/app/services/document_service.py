"""资料管理业务服务：保存文件、解析文本、切分文本、写入数据库。"""
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import UPLOAD_DIR
from app.repositories import document_repository
from app.utils.file_utils import validate_file_extension, generate_storage_filename, save_upload_file
from app.utils.text_utils import clean_text, split_text

class DocumentService:
    """资料管理业务服务。"""
    async def upload_document(self, file: UploadFile) -> dict:
        """上传并处理学习资料。"""
        if not file.filename:
            raise HTTPException(status_code=400, detail='文件名不能为空。')
        file_type = validate_file_extension(file.filename)
        storage_filename = generate_storage_filename(file.filename)
        target_path = UPLOAD_DIR / storage_filename
        await save_upload_file(file, target_path)
        raw_text = self.extract_text(target_path, file_type)
        text = clean_text(raw_text)
        if not text:
            raise HTTPException(status_code=400, detail='资料内容为空，无法解析。')
        chunks = split_text(text)
        document_id = document_repository.create_document(storage_filename, file.filename, str(target_path), file_type, len(chunks))
        document_repository.create_chunks(document_id, chunks)
        return {'document_id': document_id, 'filename': file.filename, 'chunk_count': len(chunks), 'message': '上传成功'}

    def extract_text(self, file_path: Path, file_type: str) -> str:
        """根据文件类型提取文本。项目初期建议优先使用 txt/md。"""
        if file_type in {'.txt', '.md'}:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        if file_type == '.pdf':
            return self._extract_pdf_text(file_path)
        if file_type == '.docx':
            return self._extract_docx_text(file_path)
        raise HTTPException(status_code=400, detail=f'暂不支持该文件类型：{file_type}')

    def _extract_pdf_text(self, file_path: Path) -> str:
        """提取 PDF 文本。"""
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise HTTPException(status_code=500, detail='缺少 pypdf 依赖。') from exc
        reader = PdfReader(str(file_path))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)

    def _extract_docx_text(self, file_path: Path) -> str:
        """提取 Word docx 文本。"""
        try:
            from docx import Document
        except ImportError as exc:
            raise HTTPException(status_code=500, detail='缺少 python-docx 依赖。') from exc
        doc = Document(str(file_path))
        return '\n'.join(p.text for p in doc.paragraphs)

    def list_documents(self) -> dict:
        """获取资料列表。"""
        return {'items': document_repository.list_documents()}

    def list_chunks(self, document_id: int) -> dict:
        """获取资料片段。"""
        return {'items': document_repository.list_chunks_by_document(document_id)}

    def delete_document(self, document_id: int) -> dict:
        """删除资料记录、片段和本地文件。"""
        document = document_repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail='资料不存在。')
        deleted = document_repository.delete_document(document_id)
        file_path = Path(document['file_path'])
        if file_path.exists():
            file_path.unlink()
        return {'success': deleted, 'message': '资料已删除' if deleted else '资料删除失败'}

document_service = DocumentService()
