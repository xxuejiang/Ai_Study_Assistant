"""错题本数据访问层。"""
from app.core.database import get_db

def create_wrong_question(question: str, answer: str, explanation: str, difficulty: str) -> int:
    """新增错题。"""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO wrong_questions (question, answer, explanation, difficulty) VALUES (?, ?, ?, ?)",
            (question, answer, explanation, difficulty),
        )
        return int(cursor.lastrowid)

def list_wrong_questions() -> list[dict]:
    """查询错题列表。"""
    with get_db() as conn:
        rows = conn.execute("SELECT id, question, answer, explanation, difficulty, status, created_at FROM wrong_questions ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

def update_wrong_question_status(question_id: int, status: str) -> bool:
    """修改错题状态。"""
    with get_db() as conn:
        cursor = conn.execute("UPDATE wrong_questions SET status = ? WHERE id = ?", (status, question_id))
    return cursor.rowcount > 0

def delete_wrong_question(question_id: int) -> bool:
    """删除错题。"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM wrong_questions WHERE id = ?", (question_id,))
    return cursor.rowcount > 0

def count_wrong_questions() -> int:
    """统计错题数量。"""
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM wrong_questions").fetchone()
    return int(row['count'])
