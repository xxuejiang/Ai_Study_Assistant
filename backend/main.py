"""
AI 学习助手系统后端启动入口。

本文件负责创建 FastAPI 应用、注册 API 路由、初始化数据库，并配置跨域访问。
业务处理不写在 main.py 中；具体功能放在 app/services，数据库操作放在 app/repositories。
"""

import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_api import router as health_router
from app.api.chat_api import router as chat_router
from app.api.document_api import router as document_router
from app.api.question_api import router as question_router
from app.api.wrongbook_api import router as wrongbook_router
from app.api.summary_api import router as summary_router
from app.core.config import settings
from app.core.database import init_db


def _configure_console_encoding() -> None:
    """尽量将 Python 控制台输出统一为 UTF-8。

    该函数只处理运行时日志输出，不参与任何业务流程。
    在 Windows、部分 IDE 内置终端中，默认编码可能不是 UTF-8，中文日志容易出现乱码。
    Python 3.7 及以上版本的 stdout/stderr 支持 reconfigure；如果当前运行环境不支持，
    捕获异常即可，不影响服务启动。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


_configure_console_encoding()


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。

    配置重点：
    1. 启动时初始化 SQLite 数据库；
    2. 注册 CORS 跨域中间件，保证前端 Vite 服务能够访问后端接口；
    3. 注册各功能模块路由。

    CORS 说明：
    前端开发服务可能通过 127.0.0.1、localhost、局域网 IP 或 IDE 预览端口访问。
    由于本项目没有使用 Cookie 登录态，因此 allow_credentials 设置为 False，
    允许来源由 project.config.json 中的 frontend 配置统一生成。这样可以避免浏览器 OPTIONS 预检请求返回
    400 Bad Request，导致首页无法读取 /api/dashboard。
    """
    app = FastAPI(
        title="AI 学习助手系统后端",
        description="基于 FastAPI + Ollama + SQLite 的本地大模型应用。",
        version="1.0.0",
    )

    # 初始化数据库表结构。该操作具备幂等性：表已存在时不会重复创建。
    init_db()

    # 开发环境跨域配置。
    # 前端通过 Vite 运行时，浏览器会先发送 OPTIONS 预检请求。
    # 若后端没有正确允许 Origin / Method / Header，浏览器会拦截真实请求。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由。prefix="/api" 表示所有接口都以 /api 开头。
    app.include_router(health_router, prefix="/api", tags=["系统"])
    app.include_router(chat_router, prefix="/api", tags=["智能问答"])
    app.include_router(document_router, prefix="/api", tags=["资料管理"])
    app.include_router(summary_router, prefix="/api", tags=["知识总结"])
    app.include_router(question_router, prefix="/api", tags=["题目生成"])
    app.include_router(wrongbook_router, prefix="/api", tags=["错题本"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
