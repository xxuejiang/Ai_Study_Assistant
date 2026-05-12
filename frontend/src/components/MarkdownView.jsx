/**
 * MarkdownView：轻量级 Markdown 展示组件。
 *
 * v5 调整重点：
 * 1. 如果大模型把整段内容包进 ```markdown ... ```，前端会先去掉外层代码围栏；
 * 2. 代码块改成浅色背景，避免题目区域出现大块黑色，影响阅读；
 * 3. 支持题目、答案、解析等常见字段的加粗展示，适合页面展示。
 */

function normalizeContent(content) {
  let text = String(content || "").trim();

  // 大模型经常返回：```markdown\n...\n```。
  // 如果不处理，整个结果会被渲染成代码块，页面就会像截图里一样变成黑底。
  const fenceMatch = text.match(/^```(?:markdown|md|text)?\s*\n([\s\S]*?)\n```\s*$/i);
  if (fenceMatch) text = fenceMatch[1].trim();

  return text;
}

function renderInline(text) {
  const parts = [];
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }

    const value = match[0];
    if (value.startsWith("**")) {
      parts.push({ type: "bold", value: value.slice(2, -2) });
    } else if (value.startsWith("`")) {
      parts.push({ type: "code", value: value.slice(1, -1) });
    }
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push({ type: "text", value: text.slice(lastIndex) });
  }

  return parts.map((part, index) => {
    if (part.type === "bold") return <strong key={index} className="font-semibold text-slate-950">{part.value}</strong>;
    if (part.type === "code") return <code key={index} className="rounded bg-slate-100 px-1.5 py-0.5 text-[13px] text-slate-800">{part.value}</code>;
    return <span key={index}>{part.value}</span>;
  });
}

export function MarkdownView({ content = "" }) {
  const normalized = normalizeContent(content);
  if (!normalized) return null;

  const lines = normalized.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let codeBuffer = [];
  let inCode = false;

  lines.forEach((rawLine, index) => {
    const line = rawLine.trimEnd();
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {
      if (inCode) {
        blocks.push({ type: "code", value: codeBuffer.join("\n"), key: `code-${index}` });
        codeBuffer = [];
        inCode = false;
      } else {
        inCode = true;
      }
      return;
    }

    if (inCode) {
      codeBuffer.push(line);
      return;
    }

    if (!trimmed) {
      blocks.push({ type: "space", key: `space-${index}` });
      return;
    }

    if (trimmed.startsWith("### ")) {
      blocks.push({ type: "h3", value: trimmed.slice(4), key: `h3-${index}` });
      return;
    }
    if (trimmed.startsWith("## ")) {
      blocks.push({ type: "h2", value: trimmed.slice(3), key: `h2-${index}` });
      return;
    }
    if (trimmed.startsWith("# ")) {
      blocks.push({ type: "h1", value: trimmed.slice(2), key: `h1-${index}` });
      return;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      blocks.push({ type: "ul", value: trimmed.replace(/^[-*]\s+/, ""), key: `ul-${index}` });
      return;
    }

    if (/^\d+[\.、]\s*/.test(trimmed)) {
      blocks.push({ type: "ol", value: trimmed, key: `ol-${index}` });
      return;
    }

    if (/^[一二三四五六七八九十]+[、.]/.test(trimmed)) {
      blocks.push({ type: "section", value: trimmed, key: `section-${index}` });
      return;
    }

    if (trimmed.startsWith(">")) {
      blocks.push({ type: "quote", value: trimmed.replace(/^>\s?/, ""), key: `quote-${index}` });
      return;
    }

    // A. / B. / C. / D. 选项单独识别，展示成浅色选项块。
    if (/^[A-D][\.、．]\s*/.test(trimmed)) {
      blocks.push({ type: "option", value: trimmed, key: `option-${index}` });
      return;
    }

    blocks.push({ type: "p", value: trimmed, key: `p-${index}` });
  });

  if (inCode && codeBuffer.length) {
    blocks.push({ type: "code", value: codeBuffer.join("\n"), key: "code-last" });
  }

  return (
    <div className="markdown-view space-y-2 text-sm leading-7 text-slate-800">
      {blocks.map((block) => {
        if (block.type === "space") return <div key={block.key} className="h-1" />;
        if (block.type === "h1") return <h1 key={block.key} className="pt-2 text-xl font-bold text-slate-950">{renderInline(block.value)}</h1>;
        if (block.type === "h2") return <h2 key={block.key} className="mt-4 rounded-xl bg-blue-50 px-3 py-2 text-base font-bold text-blue-950 ring-1 ring-blue-100">{renderInline(block.value)}</h2>;
        if (block.type === "h3") return <h3 key={block.key} className="pt-1 text-base font-semibold text-slate-900">{renderInline(block.value)}</h3>;
        if (block.type === "section") return <div key={block.key} className="mt-3 rounded-xl bg-white px-3 py-2 font-semibold text-slate-950 ring-1 ring-slate-200">{renderInline(block.value)}</div>;
        if (block.type === "ul") return <div key={block.key} className="flex gap-2"><span className="mt-0.5 text-blue-600">•</span><span>{renderInline(block.value)}</span></div>;
        if (block.type === "ol") return <div key={block.key} className="flex gap-2"><span className="mt-0.5 text-blue-600">•</span><span>{renderInline(block.value)}</span></div>;
        if (block.type === "quote") return <blockquote key={block.key} className="rounded-xl border-l-4 border-blue-300 bg-blue-50 px-3 py-2 text-slate-700">{renderInline(block.value)}</blockquote>;
        if (block.type === "option") return <div key={block.key} className="rounded-xl border border-slate-200 bg-white px-3 py-2">{renderInline(block.value)}</div>;
        if (block.type === "code") return <pre key={block.key} className="overflow-x-auto rounded-xl border border-slate-200 bg-slate-100 p-4 text-xs leading-6 text-slate-800">{block.value}</pre>;
        return <p key={block.key}>{renderInline(block.value)}</p>;
      })}
    </div>
  );
}
