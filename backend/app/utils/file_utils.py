"""文件处理工具函数。"""
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from app.core.config import settings

def get_file_extension(filename: str) -> str:
    """获取文件扩展名，并统一转成小写。"""
    return Path(filename).suffix.lower()

def validate_file_extension(filename: str) -> str:
    """校验文件格式是否允许上传。"""
    ext = get_file_extension(filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed = "、".join(sorted(settings.ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"暂不支持该文件格式，仅支持：{allowed}")
    return ext

def generate_storage_filename(original_filename: str) -> str:
    """生成服务器保存用文件名，避免原始文件名重复或包含特殊字符。"""
    return f"{uuid4().hex}{get_file_extension(original_filename)}"

async def save_upload_file(file: UploadFile, target_path: Path) -> None:
    """保存上传文件。"""
    content = await file.read()
    target_path.write_bytes(content)
