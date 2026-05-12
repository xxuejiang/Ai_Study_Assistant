"""聊天记录数据访问层。

Repository 层只负责数据库增删改查，不负责业务判断，也不调用大模型。
这样做的好处是：如果以后要把 SQLite 换成 MySQL，只需要重点改 repository 层。
"""

from app.core.database import get_db


def create_chat_message(user_message: str, assistant_answer: str, use_rag: bool, model: str) -> int:
    """保存一条聊天记录，并返回新记录 id。"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_messages (user_message, assistant_answer, use_rag, model)
            VALUES (?, ?, ?, ?)
            """,
            (user_message, assistant_answer, 1 if use_rag else 0, model),
        )
        return int(cursor.lastrowid)


def list_recent_chat_messages(limit: int = 30) -> list[dict]:
    """查询最近聊天记录。

    这里按 id 倒序返回，越新的记录越靠前。
    前端历史列表直接展示该结果即可。
    """
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, user_message, assistant_answer, use_rag, model, created_at
            FROM chat_messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_chat_message(message_id: int) -> bool:
    """删除单条聊天记录。"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM chat_messages WHERE id = ?", (message_id,))
    return cursor.rowcount > 0


def clear_chat_messages() -> int:
    """清空全部聊天记录，返回删除数量。"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM chat_messages")
    return cursor.rowcount


def count_chat_messages() -> int:
    """统计聊天记录数量，供首页仪表盘使用。"""
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM chat_messages").fetchone()
    return int(row["count"])
