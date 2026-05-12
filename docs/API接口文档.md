# API 接口文档

后端基础地址：

```text
http://127.0.0.1:8000/api
```

## 1. 系统接口

| 方法 | 地址 | 说明 |
|---|---|---|
| GET | /health | 后端健康检查 |
| GET | /model/status | 检查 Ollama 状态 |
| GET | /dashboard | 首页统计信息 |

## 2. 智能问答

### 2.1 发起问答

```text
POST /chat
```

请求示例：

```json
{
  "message": "什么是数据库事务？",
  "use_rag": false,
  "model": "qwen2.5:0.5b"
}
```

返回示例：

```json
{
  "id": 1,
  "answer": "## 一、简明回答\n数据库事务是……",
  "sources": [],
  "model": "qwen2.5:0.5b",
  "use_rag": false
}
```

### 2.2 查询聊天历史

```text
GET /chat/history?limit=30
```

### 2.3 删除聊天历史

```text
DELETE /chat/history/{id}
```

### 2.4 清空聊天历史

```text
DELETE /chat/history
```

## 3. 资料管理

| 方法 | 地址 | 说明 |
|---|---|---|
| POST | /documents/upload | 上传资料 |
| GET | /documents | 查询资料列表 |
| GET | /documents/{document_id}/chunks | 查询资料片段 |
| DELETE | /documents/{document_id} | 删除资料 |

## 4. 知识总结

```text
POST /summary
```

请求示例：

```json
{
  "topic": "数据库事务",
  "use_rag": true,
  "model": "qwen2.5:0.5b"
}
```

## 5. 题目生成

```text
POST /questions/generate
```

请求示例：

```json
{
  "topic": "数据库事务",
  "question_type": "选择题",
  "difficulty": "中等",
  "count": 5,
  "model": "qwen2.5:0.5b"
}
```

## 6. AI 生成历史

题目生成和知识总结统一保存到 `generation_records` 表。

| 方法 | 地址 | 说明 |
|---|---|---|
| GET | /generations | 查询全部生成历史 |
| GET | /generations?record_type=question | 只查询题目生成历史 |
| GET | /generations?record_type=summary | 只查询知识总结历史 |
| DELETE | /generations/{id} | 删除一条生成历史 |

## 7. 错题本

| 方法 | 地址 | 说明 |
|---|---|---|
| GET | /wrong-questions | 查询错题列表 |
| POST | /wrong-questions | 新增错题 |
| PATCH | /wrong-questions/{question_id}/status | 修改错题状态 |
| DELETE | /wrong-questions/{question_id} | 删除错题 |

---

# v4 接口补充

## 题目生成接口新增字段

请求地址：

```text
POST /api/questions/generate
```

新增字段：

```json
{
  "document_id": 1
}
```

说明：

- `document_id` 为空：按知识点生成，并尝试从全部资料中检索上下文；
- `document_id` 不为空：优先根据指定资料生成题目；
- 指定资料但关键词未命中时，后端会默认取该资料前几个片段作为上下文，避免完全脱离资料。

完整示例：

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

## 知识总结接口新增字段

请求地址：

```text
POST /api/summary
```

完整示例：

```json
{
  "topic": "数据库事务",
  "use_rag": true,
  "document_id": 1,
  "model": "qwen2.5:0.5b"
}
```

## 生成历史记录新增字段

`generation_records` 表新增：

```text
document_id
```

用于记录题目生成或知识总结是否绑定了某份资料。

---

# v5 题目生成接口补充

`POST /api/questions/generate` 返回值新增字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| used_fallback | boolean | 是否启用了后端格式兜底。true 表示模型原始输出未通过格式校验，系统自动整理为标准题目格式。 |

后端处理流程：

```text
接收题目生成参数
  ↓
确定资料来源：优先使用 document_id，没有则使用最新上传资料
  ↓
调用 Ollama 生成题目
  ↓
清洗 Markdown 外层代码围栏
  ↓
校验题型、数量、题干、答案、解析
  ↓
不合格时启用兜底题目生成
  ↓
保存 generation_records
  ↓
返回前端
```


## 模型列表接口

### GET /api/models

用于前端页面直接切换模型。接口会返回 Ollama 本机已安装模型、课程推荐模型和前端下拉框选项。

返回示例：

```json
{
  "available": true,
  "default_model": "qwen2.5:0.5b",
  "installed_models": ["qwen2.5:0.5b"],
  "recommended_models": ["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b"],
  "options": [
    {"name": "qwen2.5:0.5b", "installed": true, "label": "qwen2.5:0.5b（已安装）"}
  ]
}
```

说明：选择未安装模型前，需要先执行：

```bash
ollama pull qwen2.5:1.5b
```
