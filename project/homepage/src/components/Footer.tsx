import { Code2, Mail, Rss } from "lucide-react";
import { SITE_CONFIG } from "../site.config";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">
      <div className="mx-auto flex max-w-2xl justify-center gap-4">
        <a
          href={SITE_CONFIG.links.github}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 hover:text-slate-900 dark:hover:text-white"
        >
          <Code2 size={14} /> GitHub
        </a>
        <a
          href={SITE_CONFIG.links.blog}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 hover:text-slate-900 dark:hover:text-white"
        >
          <Rss size={14} /> 博客
        </a>
        <a
          href={`mailto:${SITE_CONFIG.links.email}`}
          className="flex items-center gap-1 hover:text-slate-900 dark:hover:text-white"
        >
          <Mail size={14} /> 联系我
        </a>
      </div>
      <p className="mt-3">
        © {new Date().getFullYear()} {SITE_CONFIG.name}
      </p>
    </footer>
  );
}
