"""练习题生成业务服务。"""

from fastapi import HTTPException
from app.core.config import settings
from app.repositories.document_repository import get_document, get_first_document
from app.repositories.generation_repository import create_generation_record
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.utils.prompt_templates import build_question_prompt
from app.utils.question_formatter import normalize_or_fallback_question_content
from app.utils.text_utils import build_generation_material


class QuestionService:
    """练习题生成服务。

    当前实现采用“资料片段 → 资料要点 → 题目生成 → 格式校验”的流程。
    这样做可以降低本地小模型直接处理长文本、混乱题库文本时的跑偏概率。
    """

    def _resolve_document_id(self, document_id: int | None) -> int | None:
        """确定本次生成实际使用的资料 ID。"""
        if document_id is not None:
            if not get_document(document_id):
                raise HTTPException(status_code=404, detail="指定资料不存在。")
            return document_id

        default_document = get_first_document()
        return int(default_document["id"]) if default_document else None

    def generate(
        self,
        topic: str,
        question_type: str,
        difficulty: str,
        count: int,
        model: str | None = None,
        document_id: int | None = None,
    ) -> dict:
        """根据知识点生成练习题，并保存生成记录。"""
        model_name = model or settings.DEFAULT_MODEL
        resolved_document_id = self._resolve_document_id(document_id)

        # 先检索资料片段，再从片段中整理出更适合生成题目的资料要点。
        sources = rag_service.retrieve(topic, document_id=resolved_document_id) if resolved_document_id else []
        raw_context = rag_service.build_context(sources) if sources else None
        generation_context, knowledge_units = build_generation_material(raw_context or "", topic, count)
        context = generation_context or raw_context

        # 大模型负责生成初稿；后端负责清洗输入、校验输出和必要时兜底。
        messages = build_question_prompt(topic, question_type, difficulty, count, context)
        raw_content = llm_service.chat(messages, model_name)

        content, used_fallback = normalize_or_fallback_question_content(
            raw_content=raw_content,
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            count=count,
            context=context,
            knowledge_units=knowledge_units,
        )

        record_id = create_generation_record(
            record_type="question",
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            question_count=count,
            document_id=resolved_document_id,
            content=content,
            model=model_name,
        )

        return {
            "id": record_id,
            "content": content,
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
            "used_fallback": used_fallback,
        }


question_service = QuestionService()
