"""SQLite 数据库初始化与连接管理。

本文件属于 core 层，负责整个后端项目最基础的数据库能力。
设计重点：业务代码不直接关心数据库文件在哪里，统一通过这里获取连接。
"""

import sqlite3
from contextlib import contextmanager
from app.core.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """获取 SQLite 数据库连接。

    row_factory = sqlite3.Row 的作用：
    1. 默认查询结果是 tuple，只能通过下标读取；
    2. 设置 row_factory 后，查询结果可以像字典一样读取字段；
    3. repository 层可以直接 dict(row)，更适合返回给 API。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库上下文管理器。

    统一处理 commit、rollback、close，避免业务代码中反复写样板代码。
    - 正常执行：自动提交事务；
    - 出现异常：自动回滚事务；
    - 无论成功失败：最后都会关闭连接。
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """判断某张表是否已经存在指定字段。

    这个函数用于轻量级数据库迁移：旧版本数据库已经创建过表，
    但新版本代码增加了字段时，不能只靠 CREATE TABLE IF NOT EXISTS。
    """
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row["name"] == column_name for row in rows)


def _run_lightweight_migrations(conn: sqlite3.Connection) -> None:
    """执行轻量级数据库迁移。

    当前迁移内容：
    - generation_records 增加 document_id 字段，用于记录题目/总结来自哪份资料。

    设计说明：真实项目通常会用 Alembic 做数据库迁移，
    项目为了降低复杂度，采用这种简单可读的迁移方式。
    """
    if not _column_exists(conn, "generation_records", "document_id"):
        conn.execute("ALTER TABLE generation_records ADD COLUMN document_id INTEGER")


def init_db() -> None:
    """初始化数据库表。

    FastAPI 启动时会调用本函数。
    CREATE TABLE IF NOT EXISTS 的含义：
    - 第一次启动时创建表；
    - 后续再次启动时，如果表已经存在，不会重复创建，也不会清空数据。
    """
    with get_db() as conn:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_answer TEXT NOT NULL,
                use_rag INTEGER NOT NULL DEFAULT 0,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS generation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_type TEXT NOT NULL,
                topic TEXT NOT NULL,
                question_type TEXT,
                difficulty TEXT,
                question_count INTEGER,
                document_id INTEGER,
                content TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS wrong_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                explanation TEXT,
                difficulty TEXT,
                status TEXT NOT NULL DEFAULT '未掌握',
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
            """
        )
        _run_lightweight_migrations(conn)
