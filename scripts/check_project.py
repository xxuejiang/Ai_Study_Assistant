"""
项目结构、后端语法与关键符号检查脚本。

运行方式：
    python scripts/check_project.py

作用：
1. 检查关键目录和文件是否存在；
2. 编译后端 Python 文件，检查明显语法错误；
3. 静态检查关键配置符号是否存在，例如 settings、DB_PATH、UPLOAD_DIR；
4. 静态检查常见本地导入路径是否对应真实文件。

说明：
本脚本不启动 FastAPI，也不调用 Ollama，只做静态检查，适合实际使用中快速确认项目文件是否完整。
"""
from __future__ import annotations

import ast
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

REQUIRED_PATHS = [
    "backend/main.py",
    "backend/requirements.txt",
    "backend/app/api/chat_api.py",
    "backend/app/api/question_api.py",
    "backend/app/api/summary_api.py",
    "backend/app/services/chat_service.py",
    "backend/app/services/question_service.py",
    "backend/app/services/summary_service.py",
    "backend/app/services/generation_service.py",
    "backend/app/repositories/chat_repository.py",
    "backend/app/repositories/generation_repository.py",
    "backend/app/repositories/document_repository.py",
    "backend/app/services/ollama_service.py",
    "backend/app/services/rag_service.py",
    "backend/app/core/config.py",
    "backend/app/core/database.py",
    "backend/app/utils/markdown_utils.py",
    "backend/app/utils/question_formatter.py",
    "frontend/package.json",
    "frontend/src/App.jsx",
    "frontend/src/components/MarkdownView.jsx",
    "frontend/src/pages/ChatPage.jsx",
    "frontend/src/pages/DocumentPage.jsx",
    "frontend/src/pages/QuestionPage.jsx",
    "frontend/src/pages/WrongBookPage.jsx",
    "README.md",
    ".editorconfig",
    ".gitattributes",
    ".vscode/settings.json",
]

REQUIRED_CONFIG_SYMBOLS = [
    "settings",
    "Settings",
    "BACKEND_DIR",
    "DATA_DIR",
    "UPLOAD_DIR",
    "DB_PATH",
]


def check_required_paths() -> bool:
    ok = True
    for path in REQUIRED_PATHS:
        full = ROOT / path
        if full.exists():
            print(f"[存在] {path}")
        else:
            print(f"[缺失] {path}")
            ok = False
    return ok


def check_python_syntax() -> bool:
    ok = True
    for py_file in BACKEND.rglob("*.py"):
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"[语法通过] {py_file.relative_to(ROOT)}")
        except py_compile.PyCompileError as exc:
            print(f"[语法错误] {py_file.relative_to(ROOT)}")
            print(exc)
            ok = False
    return ok


def exported_symbols(py_file: Path) -> set[str]:
    """读取一个 Python 文件中定义或赋值的顶层符号。"""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def module_to_file(module: str) -> Path | None:
    """把 app.xxx.yyy 转换成 backend/app/xxx/yyy.py 或 __init__.py。"""
    if not module.startswith("app"):
        return None
    rel_parts = module.split(".")
    base = BACKEND / Path(*rel_parts)
    if base.with_suffix(".py").exists():
        return base.with_suffix(".py")
    if (base / "__init__.py").exists():
        return base / "__init__.py"
    return None


def check_config_symbols() -> bool:
    ok = True
    config_file = BACKEND / "app/core/config.py"
    symbols = exported_symbols(config_file)
    for symbol in REQUIRED_CONFIG_SYMBOLS:
        if symbol in symbols:
            print(f"[配置存在] app.core.config.{symbol}")
        else:
            print(f"[配置缺失] app.core.config.{symbol}")
            ok = False
    return ok


def check_text_file_encoding() -> bool:
    """检查常见文本文件是否能按 UTF-8 读取。

    该检查主要用于避免 Windows 环境下复制、编辑文件后出现编码不一致。
    """
    ok = True
    patterns = ["*.py", "*.js", "*.jsx", "*.json", "*.md", "*.css", "*.html", "*.txt"]
    for pattern in patterns:
        for file_path in ROOT.rglob(pattern):
            if "node_modules" in file_path.parts or ".venv" in file_path.parts:
                continue
            try:
                file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                print(f"[编码异常] {file_path.relative_to(ROOT)} 不是有效 UTF-8")
                ok = False
    if ok:
        print("[编码检查] 常见文本文件均可按 UTF-8 读取")
    return ok


def check_requirements_policy() -> bool:
    """检查 requirements.txt 是否避免容易触发原生编译的写法。"""
    req_file = BACKEND / "requirements.txt"
    raw_text = req_file.read_text(encoding="utf-8")
    text = "\n".join(line for line in raw_text.splitlines() if not line.strip().startswith("#"))
    ok = True
    if "uvicorn[standard]" in text:
        print("[依赖风险] requirements.txt 不建议使用 uvicorn[standard]，可能在 Windows 环境触发原生扩展编译")
        ok = False
    if "pydantic>=" not in text:
        print("[依赖风险] requirements.txt 建议显式声明 pydantic>=2.11.0,<3.0.0")
        ok = False
    if ok:
        print("[依赖检查] requirements.txt 未发现已知高风险写法")
    return ok


def check_local_imports() -> bool:
    """检查 from app.xxx import yyy 的模块文件是否存在。"""
    ok = True
    for py_file in BACKEND.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app"):
                target_file = module_to_file(node.module)
                if not target_file:
                    print(f"[导入缺失] {py_file.relative_to(ROOT)} -> {node.module}")
                    ok = False
    if ok:
        print("[导入检查] app.* 本地模块路径均存在")
    return ok


def main() -> int:
    print("开始检查项目结构...")
    paths_ok = check_required_paths()

    print("\n开始检查后端 Python 语法...")
    syntax_ok = check_python_syntax()

    print("\n开始检查核心配置符号...")
    config_ok = check_config_symbols()

    print("\n开始检查本地导入路径...")
    imports_ok = check_local_imports()

    print("\n开始检查文本编码...")
    encoding_ok = check_text_file_encoding()

    print("\n开始检查依赖配置...")
    requirements_ok = check_requirements_policy()

    if paths_ok and syntax_ok and config_ok and imports_ok and encoding_ok and requirements_ok:
        print("\n检查通过。")
        return 0

    print("\n检查未通过，请根据上方提示修正。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
