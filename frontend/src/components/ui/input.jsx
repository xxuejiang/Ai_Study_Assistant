/** Input 输入框组件。 */
export function Input({ className = "", ...props }) {
  return <input className={`w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 ${className}`} {...props} />;
}
