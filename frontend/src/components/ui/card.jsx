/** Card 卡片组件：首页统计、聊天区域、上传区域都可以复用。 */
export function Card({ children, className = "" }) { return <div className={`rounded-2xl border border-slate-200 bg-white shadow-sm ${className}`}>{children}</div>; }
export function CardHeader({ children, className = "" }) { return <div className={`border-b border-slate-100 p-5 ${className}`}>{children}</div>; }
export function CardTitle({ children, className = "" }) { return <h2 className={`text-lg font-semibold text-slate-900 ${className}`}>{children}</h2>; }
export function CardDescription({ children, className = "" }) { return <p className={`mt-1 text-sm text-slate-500 ${className}`}>{children}</p>; }
export function CardContent({ children, className = "" }) { return <div className={`p-5 ${className}`}>{children}</div>; }
