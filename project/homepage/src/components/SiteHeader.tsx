import { Link, useLocation } from "react-router-dom";
import { Moon, Sun, Wrench } from "lucide-react";
import { useDarkMode } from "../hooks/useDarkMode";
import { SITE_CONFIG } from "../site.config";

export function SiteHeader() {
  const { isDark, toggle } = useDarkMode();
  const location = useLocation();
  const isHome = location.pathname === "/";

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <Link to="/" className="font-semibold tracking-tight">
          {SITE_CONFIG.name}
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          {!isHome && (
            <Link
              to="/"
              className="text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
            >
              首页
            </Link>
          )}
          <Link
            to="/tools"
            className="flex items-center gap-1 text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
          >
            <Wrench size={16} />
            工具箱
          </Link>
          <button
            type="button"
            onClick={toggle}
            aria-label="切换暗色模式"
            className="rounded-full p-1.5 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </nav>
      </div>
    </header>
  );
}
