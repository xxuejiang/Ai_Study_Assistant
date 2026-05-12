"""简化版 RAG 服务。基础版采用关键词检索，不直接上向量数据库。"""
from app.core.config import settings
from app.repositories.document_repository import list_all_chunks, list_chunks_by_document
from app.utils.text_utils import score_chunk


class RagService:
    """资料检索服务。

    本项目采用两种检索策略：
    1. 不指定 document_id：在全部资料片段中检索；
    2. 指定 document_id：只在某一份资料中检索。

    第二种策略用于题目生成和知识总结，能避免“明明上传了资料，但生成内容不围绕资料”的问题。
    """

    def retrieve(self, question: str, top_k: int | None = None, document_id: int | None = None) -> list[dict]:
        """根据问题检索相关资料片段。

        如果指定了 document_id，但关键词没有命中任何片段，则返回该资料前 top_k 个片段。
        这样做是为了提高运行稳定性：
        - 小模型和简单关键词检索都不完美；
        - 题目生成/总结通常更需要“整份资料的前几段上下文”；
        - 不能因为关键词没匹配到，就完全不用上传资料。
        """
        top_k = top_k or settings.RAG_TOP_K
        chunks = list_chunks_by_document(document_id) if document_id else list_all_chunks()

        scored = []
        for chunk in chunks:
            score = score_chunk(question, chunk["content"])
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        if scored:
            return [chunk for _, chunk in scored[:top_k]]

        # 指定资料时，即使命中不到关键词，也取前几个片段作为上下文。
        # 这能让“根据第一个文件生成题目/总结”的体验更稳定。
        if document_id:
            return chunks[:top_k]

        return []

    def build_context(self, chunks: list[dict]) -> str:
        """把检索到的资料片段拼接成模型上下文。"""
        parts = []
        total = 0
        for item in chunks:
            part = f"【资料：{item['filename']}，片段 {item['chunk_index']}】\n{item['content']}\n"
            if total + len(part) > settings.MAX_CONTEXT_CHARS:
                break
            parts.append(part)
            total += len(part)
        return "\n".join(parts)


rag_service = RagService()
