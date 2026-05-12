/**
 * 应用主布局组件。
 *
 * 该组件负责提供统一的侧边导航和内容区域。
 * 当前版本没有引入 React Router，页面切换由父组件维护 activePage 状态，
 * 这样可以减少依赖数量，并保持项目结构清晰。
 */
import { BookOpen, FileText, Home, MessageSquare, PenLine, ClipboardList } from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
  { key: "dashboard", label: "首页", icon: Home },
  { key: "chat", label: "智能问答", icon: MessageSquare },
  { key: "documents", label: "资料管理", icon: FileText },
  { key: "questions", label: "题目生成", icon: PenLine },
  { key: "wrongbook", label: "错题本", icon: ClipboardList },
];

export function Layout({ activePage, onChangePage, children }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-slate-200 bg-white p-4">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-600 text-white">
            <BookOpen size={22} />
          </div>
          <div>
            <h1 className="text-base font-semibold text-slate-900">AI 学习助手</h1>
            <p className="text-xs text-slate-500">本地大模型应用</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activePage === item.key;
            return (
              <Button
                key={item.key}
                variant={active ? "default" : "ghost"}
                className="w-full justify-start gap-2"
                onClick={() => onChangePage(item.key)}
              >
                <Icon size={17} />
                {item.label}
              </Button>
            );
          })}
        </nav>
      </aside>

      <main className="ml-64 min-h-screen p-8">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
