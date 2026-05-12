/** Textarea 多行输入组件。 */
export function Textarea({ className = "", ...props }) {
  return <textarea className={`w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 ${className}`} {...props} />;
}
