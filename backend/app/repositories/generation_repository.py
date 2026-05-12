"""AI 生成记录数据访问层。

本文件用于保存“题目生成”和“知识总结”的历史结果。
"""

from app.core.database import get_db


def create_generation_record(
    record_type: str,
    topic: str,
    content: str,
    model: str,
    question_type: str | None = None,
    difficulty: str | None = None,
    question_count: int | None = None,
    document_id: int | None = None,
) -> int:
    """新增一条 AI 生成记录。

    document_id 用于记录本次生成是否绑定了某份资料。
    这个字段解决的是实际使用中很常见的问题：
    生成题目时到底是凭空围绕知识点生成，还是根据某份上传资料生成。
    """
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO generation_records
            (record_type, topic, question_type, difficulty, question_count, document_id, content, model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (record_type, topic, question_type, difficulty, question_count, document_id, content, model),
        )
        return int(cursor.lastrowid)


def list_generation_records(record_type: str | None = None, limit: int = 50) -> list[dict]:
    """查询 AI 生成历史。"""
    with get_db() as conn:
        if record_type:
            rows = conn.execute(
                """
                SELECT id, record_type, topic, question_type, difficulty, question_count,
                       document_id, content, model, created_at
                FROM generation_records
                WHERE record_type = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (record_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, record_type, topic, question_type, difficulty, question_count,
                       document_id, content, model, created_at
                FROM generation_records
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]


def delete_generation_record(record_id: int) -> bool:
    """删除一条 AI 生成历史记录。"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM generation_records WHERE id = ?", (record_id,))
    return cursor.rowcount > 0


def count_generation_records() -> int:
    """统计 AI 生成记录数量。"""
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM generation_records").fetchone()
    return int(row["count"])
