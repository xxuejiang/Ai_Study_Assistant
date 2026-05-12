/** Select 下拉选择组件。 */
export function Select({ className = "", children, ...props }) {
  return <select className={`w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 ${className}`} {...props}>{children}</select>;
}
