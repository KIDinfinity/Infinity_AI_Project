#!/usr/bin/env node
// 每日 AI 资讯更新 CLI：交互式填写后写入 public/data/ainews.json
import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_PATH = path.join(__dirname, "..", "public", "data", "ainews.json");
const MAX_DAYS = 14;

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

async function loadData() {
  try {
    const raw = await readFile(DATA_PATH, "utf-8");
    return JSON.parse(raw);
  } catch {
    return { lastUpdated: todayISO(), days: [] };
  }
}

async function main() {
  const rl = createInterface({ input: stdin, output: stdout });
  const ask = (q) => rl.question(q);

  console.log("📰 添加每日 AI 资讯\n");

  const dateInput = (await ask(`日期（默认 ${todayISO()}）: `)).trim();
  const date = dateInput || todayISO();

  const summary = (await ask("一句话概括: ")).trim();

  const top3 = [];
  console.log("\n接下来输入 Top 3（最多 3 条，标题留空直接回车结束）:\n");
  for (let i = 0; i < 3; i += 1) {
    const title = (await ask(`[${i + 1}] 标题: `)).trim();
    if (!title) break;
    const source = (await ask(`[${i + 1}] 来源: `)).trim();
    const link = (await ask(`[${i + 1}] 链接: `)).trim();
    const reason = (await ask(`[${i + 1}] 为什么选它: `)).trim();
    top3.push({ title, source, link, reason });
  }

  rl.close();

  const data = await loadData();
  const otherDays = data.days.filter((d) => d.date !== date);
  const nextDays = [{ date, summary, top3 }, ...otherDays]
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, MAX_DAYS);

  const next = { lastUpdated: nextDays[0]?.date ?? date, days: nextDays };

  await writeFile(DATA_PATH, `${JSON.stringify(next, null, 2)}\n`, "utf-8");
  console.log(`\n✅ 已写入 ${DATA_PATH}（当前共 ${nextDays.length} 天）`);
}

main().catch((err) => {
  console.error("❌ 出错了:", err);
  process.exit(1);
});
