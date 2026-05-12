/** Button 基础组件：集中管理按钮样式，页面只关注按钮语义。 */
export function Button({ children, variant = "default", className = "", disabled = false, ...props }) {
  const base = "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60";
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200",
    outline: "border border-slate-300 bg-white text-slate-900 hover:bg-slate-50",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} disabled={disabled} {...props}>{children}</button>;
}
