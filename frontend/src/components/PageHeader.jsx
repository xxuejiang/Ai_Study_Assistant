/** 页面标题组件。 */
export function PageHeader({ title, description }) {
  return <div className="mb-6"><h1 className="text-2xl font-bold tracking-tight text-slate-950">{title}</h1>{description && <p className="mt-2 text-sm text-slate-500">{description}</p>}</div>;
}
