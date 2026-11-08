import { Routes, Route } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { ToolsIndexPage } from "./pages/ToolsIndexPage";
import { ToolDetailPage } from "./pages/ToolDetailPage";
import { SiteHeader } from "./components/SiteHeader";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tools" element={<ToolsIndexPage />} />
          <Route path="/tools/:slug" element={<ToolDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}
