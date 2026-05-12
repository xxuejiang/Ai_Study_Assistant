"""知识总结业务服务。"""

from fastapi import HTTPException
from app.core.config import settings
from app.repositories.document_repository import get_document, get_first_document
from app.repositories.generation_repository import create_generation_record
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.utils.markdown_utils import normalize_markdown
from app.utils.prompt_templates import build_summary_prompt


class SummaryService:
    """知识总结服务。

    v5 版本同步修复：
    - 前端没有传 document_id 时，默认使用最新上传资料；
    - 对模型返回内容做 Markdown 清洗，避免整段变成代码块。
    """

    def _resolve_document_id(self, document_id: int | None) -> int | None:
        """确定知识总结实际使用的资料 ID。"""
        if document_id is not None:
            if not get_document(document_id):
                raise HTTPException(status_code=404, detail="指定资料不存在。")
            return document_id

        default_document = get_first_document()
        return int(default_document["id"]) if default_document else None

    def summarize(
        self,
        topic: str,
        use_rag: bool = True,
        model: str | None = None,
        document_id: int | None = None,
    ) -> dict:
        """生成结构化复习总结，并保存生成历史。"""
        model_name = model or settings.DEFAULT_MODEL
        resolved_document_id = self._resolve_document_id(document_id) if use_rag else document_id
        sources = []
        context = None

        if use_rag and resolved_document_id:
            sources = rag_service.retrieve(topic, document_id=resolved_document_id)
            context = rag_service.build_context(sources) if sources else None

        summary = normalize_markdown(llm_service.chat(build_summary_prompt(topic, context), model_name))

        record_id = create_generation_record(
            record_type="summary",
            topic=topic,
            document_id=resolved_document_id,
            content=summary,
            model=model_name,
        )

        return {
            "id": record_id,
            "summary": summary,
            "sources": [
                {
                    "document_id": s["document_id"],
                    "filename": s["filename"],
                    "chunk_index": s["chunk_index"],
                    "content": s["content"],
                }
                for s in sources
            ],
            "model": model_name,
            "document_id": resolved_document_id,
        }


summary_service = SummaryService()
