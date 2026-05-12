/**
 * 智能问答页面。
 *
 * 本页用于说明前端最核心的几个概念：
 * 1. useState：保存页面状态，例如输入框内容、AI 回答、历史记录；
 * 2. useEffect：页面首次打开时自动加载聊天历史；
 * 3. fetch 封装：通过 chatApi.js 调用 FastAPI 后端；
 * 4. Markdown 渲染：把大模型输出整理成更舒服的阅读样式；
 * 5. 数据持久化：历史记录来自 SQLite，刷新页面后不会消失。
 */
import { useEffect, useState } from "react";
import { clearChatHistory, deleteChatHistoryItem, fetchChatHistory, sendChatMessage } from "@/api/chatApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/PageHeader";
import { ResultBox } from "@/components/ResultBox";
import { SourceList } from "@/components/SourceList";
import { ModelSelect } from "@/components/ModelSelect";

export function ChatPage() {
  const [message, setMessage] = useState("");
  const [useRag, setUseRag] = useState(false);
  const [model, setModel] = useState("qwen2.5:0.5b");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadHistory() {
    // 历史记录从后端数据库加载，不再依赖浏览器临时状态。
    const data = await fetchChatHistory(50);
    setHistory(data.items || []);
  }

  async function handleSend() {
    if (!message.trim()) {
      setError("请输入问题。");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const data = await sendChatMessage({ message, useRag, model });
      setAnswer(data.answer);
      setSources(data.sources || []);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function viewHistoryItem(item) {
    // 点击历史记录时，把数据库中的问答重新放回主展示区，用于验证历史记录持久化效果。
    setMessage(item.user_message);
    setAnswer(item.assistant_answer);
    setSources([]);
    setUseRag(Boolean(item.use_rag));
    setModel(item.model || model);
    setError("");
  }

  async function handleDeleteHistory(id) {
    if (!window.confirm("确认删除这条聊天记录吗？")) return;
    await deleteChatHistoryItem(id);
    await loadHistory();
  }

  async function handleClearHistory() {
    if (!window.confirm("确认清空全部聊天记录吗？")) return;
    await clearChatHistory();
    setAnswer("");
    setSources([]);
    await loadHistory();
  }

  useEffect(() => {
    loadHistory().catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <PageHeader title="智能问答" description="支持普通问答、基于资料问答和聊天历史持久化。" />

      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <Card>
          <CardHeader>
            <CardTitle>提问区域</CardTitle>
            <CardDescription>
              默认是普通问答；需要基于上传资料回答时，再勾选“基于资料回答”。
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <Textarea
              rows={6}
              placeholder="例如：什么是数据库事务？"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />

            <div className="flex flex-wrap items-center gap-3">
              <Button onClick={handleSend} disabled={loading}>
                {loading ? "生成中..." : "发送问题"}
              </Button>

              <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
                <input type="checkbox" checked={useRag} onChange={(e) => setUseRag(e.target.checked)} />
                基于资料回答
              </label>
            </div>

            {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}

            <ResultBox title="AI 回答" content={answer} />
            <SourceList sources={sources} />
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>模型设置</CardTitle>
              <CardDescription>当前模型可按需切换，前提是本机 Ollama 已安装对应模型。</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ModelSelect
                value={model}
                onChange={setModel}
                description="当前选择会作用于本次提问；如果选择未安装模型，需要先在命令行执行 ollama pull 模型名。"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle>聊天历史</CardTitle>
                  <CardDescription>历史记录保存在 SQLite 中，刷新页面后仍然存在。</CardDescription>
                </div>
                <Button variant="ghost" className="px-3" onClick={handleClearHistory}>清空</Button>
              </div>
            </CardHeader>

            <CardContent className="max-h-[560px] space-y-3 overflow-y-auto">
              {history.length === 0 && (
                <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">暂无聊天记录。</div>
              )}

              {history.map((item) => (
                <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <Badge variant={item.use_rag ? "success" : "gray"}>{item.use_rag ? "资料问答" : "普通问答"}</Badge>
                    <Badge variant="gray">{item.model}</Badge>
                  </div>

                  <div className="line-clamp-2 text-sm font-medium leading-6 text-slate-900">{item.user_message}</div>
                  <div className="mt-1 text-xs text-slate-400">{item.created_at}</div>

                  <div className="mt-3 flex gap-2">
                    <Button variant="outline" className="px-3 py-1.5" onClick={() => viewHistoryItem(item)}>查看</Button>
                    <Button variant="danger" className="px-3 py-1.5" onClick={() => handleDeleteHistory(item.id)}>删除</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
