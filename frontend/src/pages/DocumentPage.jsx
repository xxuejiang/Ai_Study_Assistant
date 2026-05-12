/**
 * 资料管理页面。
 *
 * 本页面实现“资料进入系统后的完整流程”：
 * 1. 用户在前端选择文件；
 * 2. 前端使用 FormData 上传文件；
 * 3. FastAPI 接收 UploadFile；
 * 4. 后端保存文件、提取文本、清洗文本、切分文本；
 * 5. 资料信息和文本片段写入 SQLite；
 * 6. 后续智能问答、题目生成、知识总结都可以复用这些片段。
 *
 * 这部分是 RAG 的前置环节。没有资料片段，后续就无法实现“基于资料回答”。
 */
import { useEffect, useState } from "react";
import { deleteDocument, fetchDocumentChunks, fetchDocuments, uploadDocument } from "@/api/documentApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/PageHeader";

export function DocumentPage() {
  const [documents, setDocuments] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [selected, setSelected] = useState(null);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadDocuments() {
    // 从后端读取资料列表。资料记录保存在 SQLite 中，刷新页面后不会丢失。
    const data = await fetchDocuments();
    setDocuments(data.items || []);
  }

  async function handleUpload() {
    if (!file) {
      setMessage("请先选择文件。");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const data = await uploadDocument(file);
      setMessage(`上传成功：${data.filename}，共切分 ${data.chunk_count} 个片段。`);
      setFile(null);
      await loadDocuments();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleViewChunks(doc) {
    // 查看资料片段的目的不是让用户逐字阅读，而是用于确认资料处理效果：
    // RAG 并不是把整份文件直接塞给大模型，而是先拆分成片段再检索。
    setSelected(doc);
    const data = await fetchDocumentChunks(doc.id);
    setChunks(data.items || []);
  }

  async function handleDelete(id) {
    if (!window.confirm("确认删除该资料吗？")) return;
    await deleteDocument(id);
    setChunks([]);
    setSelected(null);
    await loadDocuments();
  }

  useEffect(() => {
    loadDocuments().catch((err) => setMessage(err.message));
  }, []);

  return (
    <>
      <PageHeader title="资料管理" description="上传学习资料后，系统会自动读取文本并切分为多个片段。" />

      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>上传资料</CardTitle>
            <CardDescription>支持 txt、md、pdf、docx。建议优先使用 txt 或 md，解析速度更快。</CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <input
              type="file"
              className="block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />

            <Button onClick={handleUpload} disabled={loading}>
              {loading ? "上传处理中..." : "上传并解析"}
            </Button>

            {message && <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">{message}</div>}

            <div className="rounded-2xl bg-blue-50 p-4 text-sm leading-6 text-blue-800">
              <p className="font-medium">处理规则</p>
              <p>资料不会全部发给大模型，而是先切成片段。用户提问时，系统只取最相关的片段作为上下文。</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>资料列表</CardTitle>
            <CardDescription>点击“查看片段”可看到资料被切分后的内容。</CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-3">
              {documents.length === 0 && (
                <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">暂无资料，请先上传。</div>
              )}

              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between rounded-2xl border border-slate-200 p-4">
                  <div>
                    <div className="font-medium text-slate-900">{doc.original_filename}</div>
                    <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
                      <Badge variant="gray">{doc.file_type}</Badge>
                      <span>{doc.chunk_count} 个片段</span>
                      <span>{doc.created_at}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => handleViewChunks(doc)}>查看片段</Button>
                    <Button variant="danger" onClick={() => handleDelete(doc.id)}>删除</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {selected && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>资料片段：{selected.original_filename}</CardTitle>
            <CardDescription>这些片段就是后续 RAG 检索的基础数据。</CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {chunks.map((chunk) => (
              <div key={chunk.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-2 text-xs font-medium text-slate-500">片段 {chunk.chunk_index}</div>
                <p className="text-sm leading-7 text-slate-700">{chunk.content}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </>
  );
}
