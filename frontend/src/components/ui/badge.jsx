/** Badge 状态标签组件。 */
export function Badge({ children, variant = "default", className = "" }) {
  const variants = {
    default: "bg-blue-50 text-blue-700 ring-blue-600/20",
    success: "bg-green-50 text-green-700 ring-green-600/20",
    warning: "bg-amber-50 text-amber-700 ring-amber-600/20",
    danger: "bg-red-50 text-red-700 ring-red-600/20",
    gray: "bg-slate-100 text-slate-700 ring-slate-600/20",
  };
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${variants[variant]} ${className}`}>{children}</span>;
}
