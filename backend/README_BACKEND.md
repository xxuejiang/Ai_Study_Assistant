# 后端说明

后端采用 FastAPI 分层架构，核心目标是保持接口层、业务层、数据访问层分离。

## 1. 启动方式

进入后端目录：

```bash
cd backend
```

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境：

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖前先升级安装工具：

```bash
python -m pip install --upgrade pip setuptools wheel
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动后端：

```bash
python main.py
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 2. 分层说明

```text
api          接口层，接收请求、返回响应
services     业务层，编排资料检索、Prompt 构造、模型调用、记录保存
repositories 数据访问层，负责 SQLite 增删改查
schemas      请求与响应模型，规定前后端数据格式
core         配置与数据库初始化
utils        文件处理、文本处理、Prompt 模板等工具函数
```

## 3. 数据库说明

数据库文件：

```text
backend/data/app.db
```

首次启动后端时自动创建。主要数据表：

```text
documents            上传资料
document_chunks      资料片段
chat_messages        聊天历史
generation_records   题目生成和知识总结历史
wrong_questions      错题本
```

## 4. pydantic-core / maturin / cargo 安装错误

如果安装依赖时报以下错误：

```text
Failed building wheel for pydantic-core
Cargo build finished with exit code 101
maturin failed
```

优先按以下步骤处理：

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

如果仍然失败，删除 `.venv` 后重新创建虚拟环境。仍无法解决时，建议安装 Python 3.11 或 Python 3.12 后重新安装依赖。

## 5. 中文乱码处理

PowerShell：

```powershell
chcp 65001
$env:PYTHONUTF8="1"
```

项目文件统一按 UTF-8 保存，后端启动入口也会尝试将标准输出和标准错误调整为 UTF-8。
