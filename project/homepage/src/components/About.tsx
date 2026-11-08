import { SITE_CONFIG } from "../site.config";
import { SkillCloud } from "./SkillCloud";

export function About() {
  return (
    <section className="mx-auto max-w-2xl px-4 py-12 text-center">
      <p className="text-slate-700 dark:text-slate-300">{SITE_CONFIG.bio}</p>
      <SkillCloud />
    </section>
  );
}
