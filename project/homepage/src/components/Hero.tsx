import { Code2, Mail, Rss } from "lucide-react";
import { SITE_CONFIG } from "../site.config";

export function Hero() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-20 text-center">
      <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
        {SITE_CONFIG.name}
      </h1>
      <p className="mt-4 text-lg text-slate-600 dark:text-slate-300">
        {SITE_CONFIG.tagline}
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <a
          href={SITE_CONFIG.links.github}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 rounded-full border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
        >
          <Code2 size={16} /> GitHub
        </a>
        <a
          href={SITE_CONFIG.links.blog}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 rounded-full border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
        >
          <Rss size={16} /> 博客
        </a>
        <a
          href={`mailto:${SITE_CONFIG.links.email}`}
          className="flex items-center gap-2 rounded-full border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
        >
          <Mail size={16} /> 联系我
        </a>
      </div>
    </section>
  );
}
