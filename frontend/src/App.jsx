/** App 是前端根组件。当前页面通过 activePage 状态控制，降低项目路由复杂度。 */
import { useState } from "react";
import { Layout } from "@/components/Layout";
import { Dashboard } from "@/pages/Dashboard";
import { ChatPage } from "@/pages/ChatPage";
import { DocumentPage } from "@/pages/DocumentPage";
import { QuestionPage } from "@/pages/QuestionPage";
import { WrongBookPage } from "@/pages/WrongBookPage";

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  function renderPage() {
    if (activePage === "chat") return <ChatPage />;
    if (activePage === "documents") return <DocumentPage />;
    if (activePage === "questions") return <QuestionPage />;
    if (activePage === "wrongbook") return <WrongBookPage />;
    return <Dashboard />;
  }
  return <Layout activePage={activePage} onChangePage={setActivePage}>{renderPage()}</Layout>;
}
