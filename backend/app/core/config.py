"""项目配置文件。

端口、模型、Ollama 地址等常用配置统一从项目根目录的 project.config.json 读取。
这样做的目的：
1. 避免端口散落在多个文件中，后续修改时不容易遗漏；
2. 后端启动端口、前端开发端口、Ollama 端口保持同一个配置来源；
3. 推荐模型列表和默认模型也集中管理，修改模型时不需要改业务代码。

注意：
- 修改推荐模型列表不会影响 Ollama 服务检测；
- Ollama 是否可用只由 ollama.scheme / ollama.host / ollama.port 决定；
- 推荐模型只是页面候选项，模型真正能否运行取决于本机是否已经 ollama pull。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "project.config.json"
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "app.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _load_project_config() -> dict[str, Any]:
    """读取项目根目录配置文件。

    如果配置文件缺失或格式错误，直接抛出明确异常，避免后续以错误默认值启动。
    这样排查问题更快：看到报错就知道是 project.config.json 有问题。
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"项目配置文件不存在：{CONFIG_PATH}")

    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"项目配置文件不是合法 JSON：{CONFIG_PATH}，错误：{exc}") from exc


def _get(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """从多层字典中安全读取配置。

    示例：_get(config, "backend", "port", default=8000)
    """
    value: Any = config
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


@dataclass
class Settings:
    """项目全局配置。

    类字段使用大写名称，是为了让业务代码中 settings.BACKEND_PORT 这类写法更直观。
    业务代码只读取 settings，不直接读取 JSON 文件。
    """

    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    API_PREFIX: str = "/api"

    FRONTEND_HOST: str = "127.0.0.1"
    FRONTEND_PORT: int = 5173
    FRONTEND_PREVIEW_PORT: int = 4173

    OLLAMA_SCHEME: str = "http"
    OLLAMA_HOST: str = "127.0.0.1"
    OLLAMA_PORT: int = 11434
    OLLAMA_API_PREFIX: str = "/api"

    DEFAULT_MODEL: str = "qwen2.5:0.5b"
    RECOMMENDED_MODELS: list[str] = field(default_factory=list)

    RAG_TOP_K: int = 3
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    MAX_CONTEXT_CHARS: int = 3000
    ALLOWED_EXTENSIONS: set[str] = field(default_factory=lambda: {".txt", ".md", ".pdf", ".docx"})

    @classmethod
    def from_project_config(cls) -> "Settings":
        """根据 project.config.json 创建 Settings 对象。"""
        config = _load_project_config()
        recommended = _get(config, "models", "recommended", default=[])
        if not isinstance(recommended, list):
            recommended = []

        return cls(
            BACKEND_HOST=str(_get(config, "backend", "host", default="127.0.0.1")),
            BACKEND_PORT=int(_get(config, "backend", "port", default=8000)),
            API_PREFIX=str(_get(config, "backend", "apiPrefix", default="/api")),
            FRONTEND_HOST=str(_get(config, "frontend", "host", default="127.0.0.1")),
            FRONTEND_PORT=int(_get(config, "frontend", "port", default=5173)),
            FRONTEND_PREVIEW_PORT=int(_get(config, "frontend", "previewPort", default=4173)),
            OLLAMA_SCHEME=str(_get(config, "ollama", "scheme", default="http")),
            OLLAMA_HOST=str(_get(config, "ollama", "host", default="127.0.0.1")),
            OLLAMA_PORT=int(_get(config, "ollama", "port", default=11434)),
            OLLAMA_API_PREFIX=str(_get(config, "ollama", "apiPrefix", default="/api")),
            DEFAULT_MODEL=str(_get(config, "models", "default", default="qwen2.5:0.5b")),
            RECOMMENDED_MODELS=[str(item) for item in recommended],
            RAG_TOP_K=int(_get(config, "rag", "topK", default=3)),
            CHUNK_SIZE=int(_get(config, "rag", "chunkSize", default=800)),
            CHUNK_OVERLAP=int(_get(config, "rag", "chunkOverlap", default=120)),
            MAX_CONTEXT_CHARS=int(_get(config, "rag", "maxContextChars", default=3000)),
        )

    @property
    def OLLAMA_BASE_URL(self) -> str:
        """Ollama 根地址。

        示例：http://127.0.0.1:11434
        不要在 project.config.json 里把 apiPrefix 拼到 host 或 port 里。
        """
        return f"{self.OLLAMA_SCHEME}://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"

    @property
    def OLLAMA_API_BASE_URL(self) -> str:
        """Ollama API 地址。

        示例：http://127.0.0.1:11434/api
        """
        prefix = self.OLLAMA_API_PREFIX.strip("/")
        return f"{self.OLLAMA_BASE_URL}/{prefix}" if prefix else self.OLLAMA_BASE_URL

    @property
    def FRONTEND_ORIGINS(self) -> list[str]:
        """本地开发环境允许跨域访问的前端 Origin 列表。"""
        return [
            f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PORT}",
            f"http://localhost:{self.FRONTEND_PORT}",
            f"http://127.0.0.1:{self.FRONTEND_PORT}",
            f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PREVIEW_PORT}",
            f"http://localhost:{self.FRONTEND_PREVIEW_PORT}",
            f"http://127.0.0.1:{self.FRONTEND_PREVIEW_PORT}",
        ]


settings = Settings.from_project_config()
