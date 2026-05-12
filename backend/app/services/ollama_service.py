"""Ollama 服务封装。

本模块只负责和 Ollama HTTP API 通信，不处理智能问答、资料检索等业务流程。
业务层只需要调用 ollama_service.chat / ollama_service.list_models，不直接拼接 Ollama URL。
"""

from __future__ import annotations

import requests

from app.core.config import settings


class OllamaService:
    """Ollama HTTP API 客户端。

    关键约定：
    - base_url 必须是 Ollama 根地址，例如 http://127.0.0.1:11434；
    - 不要传 http://127.0.0.1:11434/api，否则会导致 /api/api/tags；
    - 本类会自动清理末尾的 /api，减少配置错误造成的 Not Found。
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = self._normalize_base_url(base_url or settings.OLLAMA_BASE_URL)
        self.api_prefix = settings.OLLAMA_API_PREFIX.strip("/")

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """规范化 Ollama 根地址。

        常见错误是把地址写成 http://127.0.0.1:11434/api。
        这里统一去掉末尾 /api，避免后续请求变成 /api/api/tags。
        """
        value = (base_url or "").strip().rstrip("/")
        if value.endswith("/api"):
            value = value[:-4].rstrip("/")
        return value

    def _api_url(self, path: str) -> str:
        """拼接 Ollama API 地址。path 传入 tags、chat 等相对路径。"""
        clean_path = path.strip("/")
        if self.api_prefix:
            return f"{self.base_url}/{self.api_prefix}/{clean_path}"
        return f"{self.base_url}/{clean_path}"

    def is_available(self) -> bool:
        """检查 Ollama 服务是否可访问。

        优先访问 /api/tags，因为该接口既能证明 Ollama 已启动，也能证明 API 前缀正确。
        修改推荐模型列表不会影响这里的判断。
        """
        try:
            response = requests.get(self._api_url("tags"), timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> list[str]:
        """获取当前 Ollama 本机已经安装的模型列表。

        Ollama 的 /api/tags 接口返回本机已有模型。
        如果 Ollama 未启动、端口不对或接口异常，返回空列表；页面仍然可以展示推荐模型。
        """
        try:
            response = requests.get(self._api_url("tags"), timeout=5)
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            names = [item.get("name") for item in models if item.get("name")]
            return sorted(set(names))
        except requests.RequestException:
            return []

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        """调用 Ollama chat 接口。

        返回字符串而不是直接抛异常，是为了让前端能显示明确的错误提示。
        """
        model = model or settings.DEFAULT_MODEL
        payload = {"model": model, "messages": messages, "stream": False}

        try:
            response = requests.post(self._api_url("chat"), json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip() or "模型没有返回有效内容。"
        except requests.ConnectionError:
            return f"Ollama 服务不可用。请确认 Ollama 已启动，并执行：\n\nollama run {model}\n"
        except requests.Timeout:
            return "调用 Ollama 超时。可能是模型过大、电脑性能较弱，或输入内容过长。"
        except requests.HTTPError as exc:
            code = getattr(exc.response, "status_code", "unknown")
            text = getattr(exc.response, "text", "")
            return (
                f"调用 Ollama 时发生 HTTP 错误，状态码：{code}。\n"
                f"当前模型：{model}\n"
                f"Ollama 地址：{self._api_url('chat')}\n"
                f"错误信息：{text[:300]}"
            )
        except requests.RequestException as exc:
            return f"调用 Ollama 失败：{exc}"


ollama_service = OllamaService()
