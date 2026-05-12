/**
 * 错题本页面。
 *
 * 本页用于说明 SQLite 的增删改查：
 * - 新增错题：INSERT；
 * - 查询错题：SELECT；
 * - 修改状态：UPDATE；
 * - 删除错题：DELETE。
 *
 * 错题记录全部保存在后端 SQLite 数据库，页面刷新后仍然存在。
 */
import { useEffect, useState } from "react";
import { createWrongQuestion, deleteWrongQuestion, fetchWrongQuestions, updateWrongQuestionStatus } from "@/api/wrongbookApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { PageHeader } from "@/components/PageHeader";
import { MarkdownView } from "@/components/MarkdownView";

export function WrongBookPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ question: "", answer: "", explanation: "", difficulty: "中等" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadItems() {
    const data = await fetchWrongQuestions();
    setItems(data.items || []);
  }

  function updateForm(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleCreate() {
    if (!form.question.trim() || !form.answer.trim()) {
      setMessage("题目和答案不能为空。");
      return;
    }

    try {
      await createWrongQuestion(form);
      setMessage("错题已保存。");
      setError("");
      setForm({ question: "", answer: "", explanation: "", difficulty: "中等" });
      await loadItems();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUpdateStatus(id, status) {
    await updateWrongQuestionStatus(id, status);
    await loadItems();
  }

  async function handleDelete(id) {
    if (!window.confirm("确认删除该错题吗？")) return;
    await deleteWrongQuestion(id);
    await loadItems();
  }

  useEffect(() => {
    loadItems().catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <PageHeader title="错题本" description="保存题目、答案、解析和掌握状态，是数据库增删改查的典型功能。" />

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>新增错题</CardTitle>
            <CardDescription>可以手动录入，也可以从 AI 生成结果中复制整理。</CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">题目</div>
              <Textarea rows={4} value={form.question} onChange={(e) => updateForm("question", e.target.value)} />
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">答案</div>
              <Input value={form.answer} onChange={(e) => updateForm("answer", e.target.value)} />
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">解析</div>
              <Textarea rows={3} value={form.explanation} onChange={(e) => updateForm("explanation", e.target.value)} />
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">难度</div>
              <Select value={form.difficulty} onChange={(e) => updateForm("difficulty", e.target.value)}>
                <option>简单</option>
                <option>中等</option>
                <option>较难</option>
              </Select>
            </div>

            <Button onClick={handleCreate}>保存错题</Button>
            {message && <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">{message}</div>}
            {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>错题列表</CardTitle>
            <CardDescription>错题列表来自数据库，刷新页面后不会丢失。</CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {items.length === 0 && <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">暂无错题。</div>}

            {items.map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Badge variant={item.status === "已掌握" ? "success" : "warning"}>{item.status}</Badge>
                  <Badge variant="gray">{item.difficulty || "中等"}</Badge>
                  <span className="text-xs text-slate-400">{item.created_at}</span>
                </div>

                <div className="font-medium leading-7 text-slate-900">{item.question}</div>
                <div className="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">答案：{item.answer}</div>

                {item.explanation && (
                  <div className="mt-2 rounded-xl bg-slate-50 p-3">
                    <MarkdownView content={item.explanation} />
                  </div>
                )}

                <div className="mt-4 flex gap-2">
                  <Button variant="outline" onClick={() => handleUpdateStatus(item.id, item.status === "已掌握" ? "未掌握" : "已掌握")}>
                    {item.status === "已掌握" ? "标记未掌握" : "标记已掌握"}
                  </Button>
                  <Button variant="danger" onClick={() => handleDelete(item.id)}>删除</Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
