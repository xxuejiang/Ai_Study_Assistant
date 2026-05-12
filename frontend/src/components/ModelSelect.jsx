/**
 * 模型选择组件。
 *
 * 设计目的：
 * 1. 把“模型怎么切换”做成页面可见的下拉框，而不是让用户去改代码；
 * 2. 优先展示 Ollama 本机已经安装的模型；
 * 3. 同时展示项目推荐模型，便于区分“已安装模型”和“可选模型”；
 * 4. 保留手动输入能力，避免用户使用自定义模型名时被下拉框限制。
 */
import { useEffect, useState } from "react";
import { fetchModelList } from "@/api/systemApi";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

export function ModelSelect({ value, onChange, description = "" }) {
  const [models, setModels] = useState([]);
  const [available, setAvailable] = useState(false);
  const [manual, setManual] = useState(false);
  const [error, setError] = useState("");

  async function loadModels() {
    try {
      const data = await fetchModelList();
      setModels(data.options || []);
      setAvailable(Boolean(data.available));
      setError("");

      if (!value && data.default_model) {
        onChange(data.default_model);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadModels();
    // 这里只在组件首次加载时获取模型列表。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <div className="text-sm font-medium text-slate-700">模型</div>
        <Button type="button" variant="ghost" className="px-2 py-1 text-xs" onClick={() => setManual(!manual)}>
          {manual ? "使用下拉选择" : "手动输入"}
        </Button>
      </div>

      {!manual ? (
        <Select value={value} onChange={(e) => onChange(e.target.value)}>
          {models.length === 0 && <option value={value}>{value || "未获取到模型列表"}</option>}
          {models.map((item) => (
            <option key={item.name} value={item.name}>
              {item.label}
            </option>
          ))}
        </Select>
      ) : (
        <Input value={value} onChange={(e) => onChange(e.target.value)} placeholder="例如：qwen2.5:0.5b" />
      )}

      <p className="text-xs leading-5 text-slate-500">
        {description || "切换模型前，需要先在本机 Ollama 中下载对应模型，例如：ollama pull qwen2.5:1.5b。"}
      </p>
      {!available && <p className="text-xs leading-5 text-amber-600">未检测到 Ollama 服务，请先启动 Ollama。</p>}
      {error && <p className="text-xs leading-5 text-red-600">模型列表加载失败：{error}</p>}
    </div>
  );
}
