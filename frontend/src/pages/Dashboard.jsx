/** 首页仪表盘。展示后端、模型、资料、聊天历史、生成历史、错题等系统状态。 */
import { useEffect, useState } from "react";
import { Brain, Database, FileText, MessageSquare, NotebookTabs, Server } from "lucide-react";
import { fetchDashboard } from "@/api/systemApi";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/PageHeader";

export function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setDashboard(await fetchDashboard());
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const cards = [
    { title: "后端服务", value: error ? "异常" : "正常", description: error || "FastAPI 服务已连接", icon: Server, badge: error ? "danger" : "success" },
    { title: "本地模型", value: dashboard?.ollama_available ? "可用" : "未连接", description: `默认：${dashboard?.default_model || "qwen2.5:0.5b"}；已安装：${dashboard?.installed_model_count ?? 0}`, icon: Brain, badge: dashboard?.ollama_available ? "success" : "warning" },
    { title: "学习资料", value: dashboard?.document_count ?? "-", description: "已上传资料数量", icon: FileText, badge: "default" },
    { title: "聊天记录", value: dashboard?.chat_count ?? "-", description: "智能问答历史数量", icon: MessageSquare, badge: "default" },
    { title: "生成记录", value: dashboard?.generation_count ?? "-", description: "题目和总结历史数量", icon: NotebookTabs, badge: "default" },
    { title: "错题数量", value: dashboard?.wrong_question_count ?? "-", description: "错题本记录数量", icon: Database, badge: "default" },
  ];

  return (
    <>
      <PageHeader title="AI 学习助手系统" description="基于 React + FastAPI + Ollama + SQLite 的本地大模型应用。" />

      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        {cards.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.title}>
              <CardContent className="p-5">
                <div className="mb-4 flex items-center justify-between">
                  <div className="rounded-2xl bg-slate-100 p-3 text-slate-700"><Icon size={20} /></div>
                  <Badge variant={item.badge}>{item.value}</Badge>
                </div>
                <div className="text-sm text-slate-500">{item.title}</div>
                <div className="mt-1 text-xl font-semibold text-slate-900">{item.value}</div>
                <div className="mt-2 text-xs text-slate-500">{item.description}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>系统架构</CardTitle>
          <CardDescription>展示系统从前端请求到后端处理、模型调用和数据存储的完整链路。</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-5">
            {["前端页面", "FastAPI 接口", "Service 业务层", "Ollama 模型", "SQLite 数据库"].map((item, index) => (
              <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-center">
                <div className="mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">{index + 1}</div>
                <div className="text-sm font-medium text-slate-800">{item}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </>
  );
}
