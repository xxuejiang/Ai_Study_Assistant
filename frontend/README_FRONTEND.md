# 前端说明

前端采用 React + Vite + JavaScript + Tailwind CSS。

## 启动

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

## 页面说明

```text
Dashboard       首页，展示系统状态和统计数量
ChatPage        智能问答，支持普通问答、资料问答、聊天历史
DocumentPage    资料管理，上传资料、查看资料片段
QuestionPage    题目生成与知识总结，支持生成历史
WrongBookPage   错题本，支持增删改查
```

## 关键组件

```text
ResultBox       统一展示大模型输出
MarkdownView    轻量级 Markdown 渲染组件，避免页面直接显示星号和井号
SourceList      展示 RAG 检索到的资料依据
```

本项目没有引入 React Router，页面切换由 App.jsx 中的 activePage 控制。
