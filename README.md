# AI 学习助手系统

## 1. 项目定位

本项目是一个面向学习辅助场景的 AI 学习助手系统，采用前后端分离架构实现。

系统主线：

```text
前端页面 → FastAPI 后端 → Ollama 本地大模型 → 学习资料检索 → SQLite 数据库存储
```

本版本已实现：

1. 普通 AI 问答；
2. 基于学习资料的 AI 问答；
3. 学习资料上传、解析、切分；
4. 知识点总结；
5. 练习题生成；
6. 聊天历史持久化；
7. 题目生成/知识总结历史持久化；
8. 错题本增删改查；
9. Markdown 结果渲染，避免页面直接显示杂乱的星号、井号；
10. 首页统计资料数量、聊天记录数量、生成记录数量、错题数量。

---

## 2. 技术栈说明

### 2.1 前端

```text
React + Vite + JavaScript + Tailwind CSS + shadcn/ui 风格本地组件
```

技术作用：

| 技术 | 作用 |
|---|---|
| React | 组织页面，把页面拆成组件 |
| Vite | 启动前端开发服务 |
| JavaScript | 编写页面逻辑 |
| Tailwind CSS | 编写页面样式 |
| 本地 UI 组件 | 封装 Button、Card、Input、Textarea、Badge 等组件 |
| fetch | 调用 FastAPI 后端接口 |

本项目不使用 TypeScript、Redux、复杂路由，目的是降低运行环境复杂度。

### 2.2 后端

```text
FastAPI + SQLite + Ollama + 分层架构
```

技术作用：

| 技术 | 作用 |
|---|---|
| FastAPI | 提供后端 API 接口 |
| SQLite | 保存资料、资料片段、聊天记录、生成记录、错题 |
| Ollama | 本地运行大模型 |
| Qwen 小模型 | 默认推荐 qwen2.5:0.5b，可替换更大模型 |
| 简化版 RAG | 采用关键词检索实现“基于资料回答” |

---

## 3. 系统架构

```text
浏览器前端
React + Vite + Tailwind + UI 组件
        ↓ HTTP / JSON
FastAPI 后端
        ↓
Service 业务层
        ↓
Ollama 本地模型 / SQLite 数据库 / 本地资料库
```

后端分层：

```text
API 层          接收请求、返回响应
Service 层      处理业务流程
Repository 层   操作数据库
Schema 层       定义请求与响应格式
Core 层         配置、数据库初始化
Utils 层        文件、文本、Prompt 等工具函数
```

类比 Java Web：

| Python/FastAPI 层 | 类比 Java Web | 职责 |
|---|---|---|
| api | Controller | 接收请求、返回响应 |
| services | Service | 处理业务逻辑 |
| repositories | DAO / Mapper | 负责数据库操作 |
| schemas | DTO / VO | 规定接口数据格式 |
| core | Config | 项目配置、数据库连接 |
| utils | Utils | 通用工具函数 |

---

## 4. 项目目录结构

```text
ai-study-assistant/
├── backend/                     # 后端项目
│   ├── main.py                  # 后端启动入口
│   ├── requirements.txt         # Python 依赖
│   ├── app/
│   │   ├── api/                 # API 接口层
│   │   ├── services/            # 业务逻辑层
│   │   ├── repositories/        # 数据访问层
│   │   ├── schemas/             # 请求/响应模型
│   │   ├── core/                # 配置与数据库初始化
│   │   └── utils/               # 工具函数、Prompt 模板
│   └── data/
│       ├── uploads/             # 上传资料保存目录
│       └── app.db               # SQLite 数据库，首次启动自动生成
│
├── frontend/                    # 前端项目
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── api/                 # 前端接口请求封装
│       ├── components/          # 公共组件和 Markdown 渲染组件
│       ├── pages/               # 页面组件
│       └── App.jsx
│
├── docs/                        # 说明和开发文档
├── scripts/                     # 检查脚本
└── README.md
```

---

## 5. 环境准备

### 5.1 基础环境

| 软件 | 推荐版本 | 作用 |
|---|---|---|
| Python | 推荐 3.11 / 3.12；Python 3.13 也可使用新版依赖 | 运行 FastAPI 后端 |
| Node.js | 18 或以上 | 运行 React 前端 |
| Ollama | 最新稳定版 | 本地运行大模型 |
| VS Code / PyCharm | 任意 | 编写代码 |

### 5.2 安装 Ollama 模型

默认模型：

```bash
ollama pull qwen2.5:0.5b
```

如果电脑性能较好：

```bash
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:3b
```

检查模型：

```bash
ollama list
ollama run qwen2.5:0.5b
```

---

## 6. 后端启动步骤

进入后端目录：

```bash
cd backend
```

创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖前，先升级安装工具，避免部分依赖触发本地编译：

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

或：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

访问：

```text
后端地址：http://127.0.0.1:8000
接口文档：http://127.0.0.1:8000/docs
健康检查：http://127.0.0.1:8000/api/health
```

---

## 7. 前端启动步骤

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

---

## 8. 推荐启动顺序

```text
第一步：确认 Ollama 已安装
第二步：ollama pull qwen2.5:0.5b
第三步：启动后端 FastAPI
第四步：启动前端 React
第五步：打开浏览器访问前端页面
第六步：先测试普通问答
第七步：上传资料后测试资料问答
第八步：测试题目生成、历史记录、错题本
```

---

## 9. 系统使用流程

### 9.1 普通 AI 问答

1. 打开前端页面；
2. 进入“智能问答”；
3. 输入问题；
4. 不勾选“基于资料回答”；
5. 点击发送；
6. 系统调用 Ollama 返回回答；
7. 问答记录自动保存到 SQLite；
8. 刷新页面后，右侧“聊天历史”仍然可以查看以前的问题和回答。

### 9.2 基于资料问答

1. 进入“资料管理”；
2. 上传 txt、md、pdf 或 docx 资料；
3. 系统自动解析并切分文本；
4. 进入“智能问答”；
5. 勾选“基于资料回答”；
6. 输入与资料相关的问题；
7. 系统先检索资料片段，再调用大模型回答；
8. 如果没有检索到相关资料，系统会自动降级为普通问答，避免完全答不出来。

### 9.3 生成练习题

1. 进入“题目生成”；
2. 输入知识点；
3. 选择题型、难度和数量；
4. 点击“生成题目”；
5. 系统调用大模型生成练习题；
6. 生成结果自动保存到 SQLite；
7. 刷新页面后，右侧“生成历史”仍然可以查看。

### 9.4 生成知识总结

1. 进入“题目生成”；
2. 输入知识点；
3. 点击“生成总结”；
4. 系统生成结构化复习总结；
5. 总结结果自动保存到生成历史。

### 9.5 错题本管理

1. 进入“错题本”；
2. 新增错题；
3. 查看错题列表；
4. 标记已掌握；
5. 删除错题；
6. 错题数据保存在 SQLite，刷新页面后仍然存在。

---

## 10. 数据库存储说明

SQLite 数据库文件：

```text
backend/data/app.db
```

数据库表：

| 表名 | 作用 |
|---|---|
| documents | 保存上传资料信息 |
| document_chunks | 保存资料切分后的文本片段 |
| chat_messages | 保存智能问答历史 |
| generation_records | 保存题目生成、知识总结历史 |
| wrong_questions | 保存错题本记录 |

如果需要重新开始测试，可以停止后端后删除：

```text
backend/data/app.db
```

再次启动后端时，系统会自动重新创建数据库表。

---

## 11. 核心接口

| 方法 | 地址 | 功能 |
|---|---|---|
| GET | /api/health | 后端健康检查 |
| GET | /api/model/status | 检查 Ollama 状态 |
| GET | /api/dashboard | 首页统计信息 |
| POST | /api/chat | AI 问答 |
| GET | /api/chat/history | 查询聊天历史 |
| DELETE | /api/chat/history/{id} | 删除单条聊天历史 |
| DELETE | /api/chat/history | 清空聊天历史 |
| POST | /api/documents/upload | 上传资料 |
| GET | /api/documents | 查看资料列表 |
| GET | /api/documents/{document_id}/chunks | 查看资料片段 |
| DELETE | /api/documents/{document_id} | 删除资料 |
| POST | /api/summary | 生成知识总结 |
| POST | /api/questions/generate | 生成练习题 |
| GET | /api/generations | 查看题目/总结生成历史 |
| DELETE | /api/generations/{id} | 删除生成历史 |
| GET | /api/wrong-questions | 查看错题 |
| POST | /api/wrong-questions | 新增错题 |
| PATCH | /api/wrong-questions/{question_id}/status | 修改错题状态 |
| DELETE | /api/wrong-questions/{question_id} | 删除错题 |

---

## 12. 系统流程

```text
用户在页面输入问题
        ↓
React 用 fetch 调用 FastAPI
        ↓
FastAPI 接收请求
        ↓
Service 层处理业务
        ↓
如果启用资料问答，则先检索资料片段
        ↓
构造 Prompt
        ↓
调用 Ollama 本地模型
        ↓
保存聊天记录或生成记录
        ↓
返回结果给前端
        ↓
React 使用 MarkdownView 渲染 AI 输出
```

说明重点：

```text
前端负责交互
后端负责业务
模型负责生成
资料检索负责提供依据
数据库负责保存记录
Markdown 渲染负责让输出更规整
```

---

## 13. 常见问题

### 13.1 前端页面无法访问后端

检查：

```text
http://127.0.0.1:8000/api/health
```

### 13.2 AI 回答提示 Ollama 不可用

检查：

```bash
ollama list
ollama run qwen2.5:0.5b
```

### 13.3 不上传资料能不能问问题

可以。智能问答默认是普通问答，不依赖上传资料。

只有勾选“基于资料回答”时，系统才会先检索资料。如果没有检索到相关资料，会自动降级为普通问答。

### 13.4 生成结果为什么之前会消失

旧版本只在页面状态中显示结果，刷新页面后状态丢失。当前版本已经把聊天记录、题目生成记录、知识总结记录、错题本记录保存到 SQLite。

### 13.5 页面上为什么不再直接显示星号和井号

当前版本增加了 `MarkdownView` 组件。大模型输出 Markdown 后，前端会把标题、列表、加粗、代码块渲染成更规整的页面样式。

### 13.6 模型回答很慢

常见原因：

1. 模型太大；
2. 没有 GPU；
3. CPU 性能较弱；
4. 输入资料片段过长。

处理方式：

1. 使用 qwen2.5:0.5b；
2. 减少资料片段长度；
3. 减少一次检索片段数量；
4. 后续替换更强硬件或更强模型。

### 13.7 小模型回答质量不高

正常现象。小模型能力有限是正常现象。后续替换更强模型时，整体架构不需要推翻。

### 13.8 安装依赖时报 pydantic-core / maturin / cargo 错误

常见报错关键词：

```text
Failed building wheel for pydantic-core
Cargo build finished with exit code 101
maturin failed
error: failed-wheel-build-for-install
```

该问题通常不是项目代码错误，而是 Python 版本、pip 缓存或依赖二进制包不匹配导致 pip 尝试本地编译 `pydantic-core`。本项目已将依赖升级为更适合 Python 3.13 的版本范围，并且不再使用 `uvicorn[standard]`，减少原生扩展安装失败概率。

处理步骤：

```bash
cd backend

# 删除旧虚拟环境后重新创建；Windows 可直接手动删除 backend/.venv 目录
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

如果仍然失败，建议安装 Python 3.11 或 Python 3.12 后重新创建虚拟环境。Python 3.11 / 3.12 的第三方包兼容性通常更稳定。

### 13.9 中文乱码处理

项目文本文件统一使用 UTF-8 编码。若 Windows 终端或 IDE 终端出现中文乱码，按以下方式处理。

PowerShell：

```powershell
chcp 65001
$env:PYTHONUTF8="1"
```

PyCharm 设置：

```text
Settings → Editor → File Encodings
Global Encoding: UTF-8
Project Encoding: UTF-8
Default encoding for properties files: UTF-8
```

VS Code 设置文件已提供：

```text
.vscode/settings.json
```

后端 `main.py` 中也增加了标准输出 UTF-8 配置，用于降低终端日志乱码概率。

---

## 14. 项目检查

```bash
python scripts/check_project.py
```

该脚本检查：

1. 关键目录是否存在；
2. 关键文件是否存在；
3. 后端 Python 文件是否存在明显语法错误。

---

## 15. 后续扩展方向

1. 向量检索版 RAG；
2. 流式输出；
3. 用户登录；
4. 学习统计；
5. 云端大模型 API；
6. React Router 多页面路由；
7. TypeScript 重构；
8. 管理端资料管理。

---

## 16. v4 修复说明

本版本重点修复以下问题：

1. **下载文件名改为英文**  
   新压缩包使用 `ai_study_assistant_v4_fixed.zip`，避免中文文件名在部分客户端中出现“无法获取上传状态”的问题。

2. **题目生成默认绑定上传资料**  
   进入“题目生成与知识总结”页面时，系统会自动读取资料管理中的资料列表。  
   如果已经上传资料，默认选择最新上传的一份资料，并自动把文件名转换为默认主题。

3. **题目生成新增 document_id 参数**  
   后端 `/api/questions/generate` 接口支持 `document_id`。  
   为空时按知识点生成；不为空时优先根据指定资料生成。

4. **知识总结新增 document_id 参数**  
   后端 `/api/summary` 接口支持 `document_id`。  
   这样总结功能也可以明确绑定某份资料。

5. **RAG 检索逻辑增强**  
   指定资料时，如果关键词没有命中任何片段，系统会默认取该资料前几个片段作为上下文。  
   这样可以避免“明明选择了资料，但模型没有基于资料生成”的情况。

6. **题型 Prompt 增强**  
   后端针对选择题、判断题、填空题、简答题分别设置了更明确的输出约束。  
   小模型仍然可能偶尔跑偏，但稳定性已经比普通 Prompt 更高。

7. **生成历史记录增加 document_id**  
   `generation_records` 表增加 `document_id` 字段，用于记录题目或总结来自哪份资料。

8. **数据库轻量迁移**  
   如果旧版本已经生成过 `app.db`，后端启动时会自动检查 `generation_records` 表是否存在 `document_id` 字段；不存在则自动追加。  
   项目不引入 Alembic，避免增加学习负担。

9. **配置导入检查**  
   项目中使用的 `from app.core.config import settings` 已完整实现。  
   `settings` 位于 `backend/app/core/config.py`，集中管理默认模型、Ollama 地址、RAG 参数、上传目录等配置。

---

## 17. 关键配置说明

配置文件位置：

```text
backend/app/core/config.py
```

核心配置：

```python
settings.DEFAULT_MODEL      # 默认模型，例如 qwen2.5:0.5b
settings.OLLAMA_BASE_URL   # Ollama 本地接口地址
settings.RAG_TOP_K         # RAG 默认返回几个资料片段
settings.CHUNK_SIZE        # 资料切分长度
settings.CHUNK_OVERLAP     # 片段重叠长度
settings.ALLOWED_EXTENSIONS # 允许上传的文件格式
```

设计说明：

> 配置不要散落在业务代码里。统一放在 config.py，后期修改模型、端口、RAG 参数时更清楚。

---

## 18. 题目生成接口示例

```json
{
  "topic": "数据库事务",
  "question_type": "选择题",
  "difficulty": "中等",
  "count": 5,
  "document_id": 1,
  "model": "qwen2.5:0.5b"
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| topic | 知识点或主题 |
| question_type | 题型：选择题、判断题、填空题、简答题 |
| difficulty | 难度：简单、中等、较难 |
| count | 题目数量 |
| document_id | 可选，指定资料 ID |
| model | 可选，模型名称 |

---

## 19. 小模型输出不稳定的说明

默认模型 `qwen2.5:0.5b` 体积小，适合 CPU 运行环境，但能力有限。可能出现：

1. 指定 5 道题，实际生成 4 道或 6 道；
2. 指定判断题，偶尔仍生成选择题格式；
3. 复杂资料总结不够深入；
4. 长上下文理解不稳定。

解决方式：

1. 优先使用更强模型，例如 `qwen2.5:1.5b` 或 `qwen2.5:3b`；
2. 缩短资料内容，减少无关文本；
3. 提高 Prompt 约束；
4. 后续增加结构化 JSON 输出校验。

本项目的核心价值在于提供完整、可替换、可扩展的 AI 应用结构：

```text
前端页面 → 后端接口 → 本地模型 → 资料检索 → 数据库存储
```

形成完整的 AI 应用开发流程。
