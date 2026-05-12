/** 资料来源展示组件。用于说明 AI 回答参考了哪些资料片段。 */
import { Badge } from "@/components/ui/badge";
export function SourceList({ sources = [] }) {
  if (!sources.length) return null;
  return <div className="mt-4 space-y-3"><div className="text-sm font-medium text-slate-700">资料依据</div>{sources.map((s, i) => <div key={`${s.document_id}-${s.chunk_index}-${i}`} className="rounded-xl border border-slate-200 bg-slate-50 p-3"><div className="mb-2 flex items-center gap-2"><Badge variant="gray">{s.filename}</Badge><span className="text-xs text-slate-500">片段 {s.chunk_index}</span></div><p className="text-sm leading-6 text-slate-600">{s.content}</p></div>)}</div>;
}
