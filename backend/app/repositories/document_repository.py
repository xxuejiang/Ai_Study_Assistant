"""资料与资料片段的数据访问层。"""
from app.core.database import get_db


def create_document(filename: str, original_filename: str, file_path: str, file_type: str, chunk_count: int) -> int:
    """新增资料记录，并返回资料 id。"""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO documents (filename, original_filename, file_path, file_type, chunk_count) VALUES (?, ?, ?, ?, ?)",
            (filename, original_filename, file_path, file_type, chunk_count),
        )
        return int(cursor.lastrowid)


def create_chunks(document_id: int, chunks: list[str]) -> None:
    """批量保存资料片段。"""
    with get_db() as conn:
        conn.executemany(
            "INSERT INTO document_chunks (document_id, chunk_index, content) VALUES (?, ?, ?)",
            [(document_id, i, c) for i, c in enumerate(chunks)],
        )


def list_documents() -> list[dict]:
    """查询全部资料。

    按 id 倒序返回，最新上传的资料在前面。
    前端如果要“默认使用第一份资料”，直接取 items[0] 即可。
    """
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, filename, original_filename, file_type, chunk_count, created_at
            FROM documents
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_first_document() -> dict | None:
    """获取默认资料。

    当前策略：取最新上传的一份资料。
    这样更符合项目使用习惯：刚上传资料后，题目生成页会自动使用它。
    """
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, filename, original_filename, file_path, file_type, chunk_count, created_at
            FROM documents
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def get_document(document_id: int) -> dict | None:
    """根据 id 查询资料。"""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, filename, original_filename, file_path, file_type, chunk_count, created_at
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def list_chunks_by_document(document_id: int) -> list[dict]:
    """查询某份资料的全部片段。"""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.content, d.original_filename AS filename
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.document_id = ?
            ORDER BY c.chunk_index ASC
            """,
            (document_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_all_chunks() -> list[dict]:
    """查询所有资料片段。简化版 RAG 会在这些片段中做关键词检索。"""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.content, d.original_filename AS filename
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_document(document_id: int) -> bool:
    """删除资料及其片段。"""
    with get_db() as conn:
        conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    return cursor.rowcount > 0
