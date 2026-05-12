/**
 * 题目生成与知识总结页面。
 *
 * v5 修复重点：
 * 1. 默认绑定资料管理中最新上传的一份资料，不再默认“不绑定资料”；
 * 2. 生成题目时，后端会对小模型输出做格式校验，必要时启用格式兜底；
 * 3. 生成结果用 MarkdownView 渲染，不再出现整块黑色代码区域；
 * 4. 历史记录继续保存到 generation_records 表，刷新页面后仍可查看。
 */
import { useEffect, useState } from "react";
import { fetchDocuments } from "@/api/documentApi";
import { deleteGenerationRecord, fetchGenerationHistory, generateQuestions, generateSummary } from "@/api/questionApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { PageHeader } from "@/components/PageHeader";
import { ResultBox } from "@/components/ResultBox";
import { SourceList } from "@/components/SourceList";
import { ModelSelect } from "@/components/ModelSelect";

function filenameToTopic(filename) {
  // 把“数据库事务.txt”转换成“数据库事务”，作为默认知识点。
  return String(filename || "").replace(/\.[^.]+$/, "");
}

export function QuestionPage() {
  const [documents, setDocuments] = useState([]);
  const [documentId, setDocumentId] = useState("");
  const [topic, setTopic] = useState("");
  const [questionType, setQuestionType] = useState("选择题");
  const [difficulty, setDifficulty] = useState("中等");
  const [count, setCount] = useState(5);
  const [model, setModel] = useState("qwen2.5:0.5b");
  const [result, setResult] = useState("");
  const [resultTitle, setResultTitle] = useState("输出内容");
  const [sources, setSources] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadDocuments() {
    const data = await fetchDocuments();
    const items = data.items || [];
    setDocuments(items);

    // 资料管理接口按 id 倒序返回，items[0] 是最新上传资料。
    // 本页默认绑定最新资料，这样可以减少手动选择资料的操作。
    if (items.length > 0) {
      const first = items[0];
      setDocumentId((current) => current || String(first.id));
      setTopic((current) => current || filenameToTopic(first.original_filename));
    }
  }

  async function loadHistory() {
    const data = await fetchGenerationHistory({ limit: 80 });
    setHistory(data.items || []);
  }

  function handleChangeDocument(value) {
    setDocumentId(value);
    const doc = documents.find((item) => String(item.id) === String(value));
    if (doc) {
      setTopic(filenameToTopic(doc.original_filename));
    }
  }

  function getSelectedDocumentName() {
    const doc = documents.find((item) => String(item.id) === String(documentId));
    return doc ? doc.original_filename : "未选择资料";
  }

  async function handleGenerateQuestions() {
    if (!topic.trim()) {
      setError("请输入知识点，或先上传资料后选择资料。");
      return;
    }

    setLoading(true);
    setError("");
    setNotice("");
    setResult("");
    setSources([]);
    setResultTitle(`生成题目：${questionType}`);

    try {
      const data = await generateQuestions({
        topic,
        questionType,
        difficulty,
        count,
        model,
        documentId: documentId ? Number(documentId) : null,
      });

      setResult(data.content);
      setSources(data.sources || []);
      if (data.document_id && !documentId) setDocumentId(String(data.document_id));
      if (data.used_fallback) {
        setNotice("本次模型原始输出格式不稳定，系统已自动整理为标准题目格式。");
      }
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateSummary() {
    if (!topic.trim()) {
      setError("请输入总结主题，或先上传资料后选择资料。");
      return;
    }

    setLoading(true);
    setError("");
    setNotice("");
    setResult("");
    setSources([]);
    setResultTitle("知识总结");

    try {
      const data = await generateSummary({
        topic,
        useRag: true,
        model,
        documentId: documentId ? Number(documentId) : null,
      });
      setResult(data.summary);
      setSources(data.sources || []);
      if (data.document_id && !documentId) setDocumentId(String(data.document_id));
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function viewHistoryItem(item) {
    setTopic(item.topic);
    setModel(item.model || model);
    setResult(item.content);
    setResultTitle(item.record_type === "summary" ? "历史知识总结" : "历史生成题目");
    setSources([]);
    if (item.document_id) setDocumentId(String(item.document_id));
    if (item.question_type) setQuestionType(item.question_type);
    if (item.difficulty) setDifficulty(item.difficulty);
    if (item.question_count) setCount(item.question_count);
    setError("");
    setNotice("");
  }

  async function handleDeleteRecord(id) {
    if (!window.confirm("确认删除这条生成记录吗？")) return;
    await deleteGenerationRecord(id);
    await loadHistory();
  }

  useEffect(() => {
    Promise.all([loadDocuments(), loadHistory()]).catch((err) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <PageHeader title="题目生成与知识总结" description="默认绑定最新上传资料，生成结果会保存为历史记录。" />

      <div className="grid gap-6 xl:grid-cols-[380px_1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle>生成参数</CardTitle>
            <CardDescription>优先选择资料，再按题型、难度和数量生成内容。</CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">资料来源</div>
              <Select value={documentId} onChange={(e) => handleChangeDocument(e.target.value)}>
                {documents.length === 0 && <option value="">暂无资料，请先到资料管理上传</option>}
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>{doc.original_filename}</option>
                ))}
              </Select>
              <p className="mt-2 text-xs leading-5 text-slate-500">
                当前资料：{documents.length > 0 ? getSelectedDocumentName() : "未上传资料"}。后端也会默认使用最新上传资料，避免模型脱离资料随意生成。
              </p>
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">知识点 / 主题</div>
              <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="例如：数据库事务" />
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">题型</div>
              <Select value={questionType} onChange={(e) => setQuestionType(e.target.value)}>
                <option value="选择题">选择题</option>
                <option value="判断题">判断题</option>
                <option value="填空题">填空题</option>
                <option value="简答题">简答题</option>
              </Select>
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">难度</div>
              <Select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="简单">简单</option>
                <option value="中等">中等</option>
                <option value="较难">较难</option>
              </Select>
            </div>

            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">数量</div>
              <Input type="number" min="1" max="20" value={count} onChange={(e) => setCount(Number(e.target.value || 1))} />
            </div>

            <ModelSelect
              value={model}
              onChange={setModel}
              description="生成题目和总结也可以直接切换模型。小模型速度快，大模型效果更好但更吃配置。"
            />

            <div className="flex gap-2">
              <Button onClick={handleGenerateQuestions} disabled={loading}>生成题目</Button>
              <Button variant="outline" onClick={handleGenerateSummary} disabled={loading}>生成总结</Button>
            </div>

            {notice && <div className="rounded-xl bg-blue-50 p-3 text-sm leading-6 text-blue-700">{notice}</div>}
            {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>生成结果</CardTitle>
            <CardDescription>结果会被渲染成标题、选项、答案和解析，不再直接显示原始 Markdown 符号。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading && <ResultBox title="生成中..." content="请稍候，正在调用本地模型。" />}
            {!loading && <ResultBox title={resultTitle} content={result} />}
            <SourceList sources={sources} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>生成历史</CardTitle>
            <CardDescription>题目和总结统一保存到 generation_records 表。</CardDescription>
          </CardHeader>

          <CardContent className="max-h-[720px] space-y-3 overflow-y-auto">
            {history.length === 0 && (
              <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">暂无生成记录。</div>
            )}

            {history.map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant={item.record_type === "summary" ? "success" : "default"}>
                    {item.record_type === "summary" ? "总结" : "题目"}
                  </Badge>
                  {item.document_id && <Badge variant="gray">资料 #{item.document_id}</Badge>}
                  {item.question_type && <Badge variant="gray">{item.question_type}</Badge>}
                  {item.difficulty && <Badge variant="gray">{item.difficulty}</Badge>}
                </div>

                <div className="line-clamp-2 text-sm font-medium leading-6 text-slate-900">{item.topic}</div>
                <div className="mt-1 text-xs text-slate-400">{item.created_at}</div>

                <div className="mt-3 flex gap-2">
                  <Button variant="outline" className="px-3 py-1.5" onClick={() => viewHistoryItem(item)}>查看</Button>
                  <Button variant="danger" className="px-3 py-1.5" onClick={() => handleDeleteRecord(item.id)}>删除</Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
