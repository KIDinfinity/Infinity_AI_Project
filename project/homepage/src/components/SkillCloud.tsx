import { SITE_CONFIG } from "../site.config";

export function SkillCloud() {
  return (
    <div className="mt-6 flex flex-wrap justify-center gap-2">
      {SITE_CONFIG.skills.map((skill) => (
        <span
          key={skill}
          className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-200"
        >
          {skill}
        </span>
      ))}
    </div>
  );
}
