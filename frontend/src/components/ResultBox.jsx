/**
 * 结果展示组件。
 *
 * ResultBox 只负责“外层容器”，真正的 Markdown 解析交给 MarkdownView。
 * 这样做的好处是：聊天、总结、题目生成都能复用同一套展示逻辑。
 */
import { MarkdownView } from "@/components/MarkdownView";

export function ResultBox({ title = "结果", content }) {
  if (!content) return null;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 border-b border-slate-100 pb-2 text-sm font-semibold text-slate-700">{title}</div>
      <MarkdownView content={content} />
    </div>
  );
}
