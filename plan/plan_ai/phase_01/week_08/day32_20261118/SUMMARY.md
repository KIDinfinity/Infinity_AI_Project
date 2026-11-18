# Day 32 执行摘要（SUMMARY）— WorkPilot 开源发布准备

> 日期：2026-11-18｜执行对象：[PLAN.md](./PLAN.md)（第 3 节 8 项验收）
> 约束遵守：**未做任何 git commit / push**；所有文件仅在工作树创建/修改，提交与推送由用户执行。
> 部署地址使用公网 IP `http://8.148.216.61`（非域名）；Caddyfile 为 IP + HTTP（无 TLS）。

---

## 一、8 项验收逐项结论

| # | 验收项 | 结论 | 说明 |
| --- | --- | --- | --- |
| 1 | gitleaks 全历史无泄露 | ✅ 通过 | `gitleaks git` 扫描 19 commits = **no leaks found**；`gitleaks dir` 仅命中 `.env`/`.env.prod`（已 gitignore、从未提交，安全） |
| 2 | 敏感词 0 命中 + `/Users/<用户名>` 路径 0 命中 | 🔴 未通过 | **发现 15 个已提交的 `eval/reports/*.json` 含绝对路径 `/Users/infinity/lab/workpilot/...`**；敏感词表需用户先填写真实词才能执行 |
| 3 | `.env`/`data/corpus/`/`*.db` 从未提交 | ✅ 通过 | `git log --all` 与 `git ls-files` 均确认空 |
| 4 | 作者邮箱非公司邮箱 | ✅ 通过 | 仅 `17855593657@163.com`（个人）+ `infinity@infinitys-MacBook-Pro.local`（本机 `.local`） |
| 5 | GitHub 仓库可访问（README/Demo GIF/mermaid/tag/LICENSE） | 🔴 未完成 | 未推送（用户执行）；且 **demo.gif 为 42 字节占位**，README 第 7 行标注「Day31 替换为真实演示录屏」 |
| 6 | 简历 ≥ 3 条带数字 P1 bullet | ✅ 通过 | 已建 4 条，数字全部取自 p1.md（hit@5 0.921 等） |
| 7 | 10 道 RAG 面试题（要点 + 证据链接） | ✅ 通过 | 已追加 10 题，每题 3–5 要点 + `证据：` 链接（路径已修正为实际路径） |
| 8 | 能力矩阵 ≥ 12 项填「由哪个模块证明」+ 提交 | 🔶 部分 | 矩阵 17 项有模块证明（≥12 达标）；**projects 仓库未提交**（用户执行） |

**结论：Task 3 保持 IN PROGRESS**，P0 为 #2（`/Users/` 路径泄露）与 #5（demo.gif 占位 + 未推送）。修复前禁止公开仓库。

---

## 二、发现的问题（需用户决策/处理）

### P0-1：`/Users/infinity/` 绝对路径泄露（违反验收 #2）
15 个已提交历史的 `eval/reports/*.json`，其 `dataset` 字段记录了本机绝对路径：
```
eval/reports/20261023-rag-baseline.json
eval/reports/20261027-exp-c300_o0.json  …（共 15 个，含 c300/c600/c1000/hybrid 各变体）
eval/reports/20261028-rag-v0.3.json
```
每行形如 `"dataset": "/Users/infinity/lab/workpilot/eval/datasets/kb_qa.jsonl"`。
**泄露信息**：macOS 用户名 `infinity` + 本机目录结构。
**建议修复**：① 把 eval 报告生成器改成写相对路径（`eval/datasets/kb_qa.jsonl`）；② 用 `git filter-repo` 重写历史。二者都属改动提交历史，须用户确认后再做（本次未动）。

### P0-2：demo.gif 为 42 字节占位（违反验收 #5）
`docs/assets/demo.gif` 仅 42 字节，README 第 7 行 `![demo](docs/assets/demo.gif) <!-- Day31 替换为真实演示录屏 -->` 仍未替换。需用户录制真实演示并覆盖，否则 GitHub 首页 demo 不显示。

### P1-1：敏感词表待用户填写
已建 `~/lab/.private/sensitive-words.txt` 模板（纯注释占位）。公司中文/英文名、产品代号、同事姓名、内网域名、工号等需用户逐行填入，否则验收 #2 的敏感词 grep 无实际意义。

### P1-2：MIT 版权人待确认
`LICENSE` 版权行写 `Copyright (c) 2026 infinity`（取自 git `user.name`）。README 已有「MIT License」字样但原先无 LICENSE 文件。请确认版权人用 `infinity` 还是 `KIDinfinity`，若改需同步 LICENSE 首行。

### P1-3：「首字延迟」数字不存在
p1.md 中**没有** first-token 延迟指标，只有 P95 总延迟 2708 ms。简历 bullet 已用 P95 代替，未杜撰 first-token 数字。

### P1-4：hit@5 无提升，勿做「提升」话术
基线 v0.2 → v0.3 的 hit@5 为 0.921 **持平**；真实改善项是「库内误拒率 0.132 → 0.053」。简历 bullet 2 已按此写，避免夸大。

---

## 三、本次生成的交付物（均未提交）

| 文件 | 说明 |
| --- | --- |
| `~/lab/workpilot/LICENSE` | MIT 全文（版权 `2026 infinity`） |
| `~/lab/.private/sensitive-words.txt` | 敏感词模板（待填真实词，放仓库外） |
| `~/lab/projects/career/resume/ai-fullstack-draft.md` | 4 条带数字 P1 bullet + 数据溯源表 |
| `~/lab/projects/career/interview-questions.md` | 追加 10 道 RAG 面试题（含证据链接） |
| `~/lab/projects/career/capability-matrix.md` | 6 项「当前水平」按证据上调 + 证据路径修正 |

---

## 四、完整验收命令（可整段复制，任意目录可跑）

```bash
# ============ 验收 #1：gitleaks 全历史无泄露 ============
brew install gitleaks 2>/dev/null          # 本次已装 8.30.1，可跳过
cd ~/lab/workpilot && gitleaks git --redact -v .        # 期望：no leaks found
cd ~/lab/workpilot && gitleaks dir --redact -v .        # 期望：仅 .env/.env.prod 命中（gitignore，安全）

# ============ 验收 #2：敏感词 + /Users/ 路径 0 命中 ============
# 先填真实敏感词：vim ~/lab/.private/sensitive-words.txt（每行一词）
cd ~/lab/workpilot && git grep -n -F -f ~/lab/.private/sensitive-words.txt $(git rev-list --all)
    # 期望：无输出（0 命中）
cd ~/lab/workpilot && git grep -n "/Users/" $(git rev-list --all) | sed 's/^[0-9a-f]*://' | sort -u
    # 当前：15 个 eval/reports/*.json 命中（P0 待修复，见上）

# ============ 验收 #3：敏感文件从未提交 ============
cd ~/lab/workpilot && git log --all --oneline -- .env .env.prod 'data/corpus/*' '*.db'
    # 期望：无输出（空）
cd ~/lab/workpilot && git ls-files | grep -E '(^|/)\.env$|(^|/)data/corpus/|\.db$'
    # 期望：无输出（空）

# ============ 验收 #4：作者邮箱非公司邮箱 ============
cd ~/lab/workpilot && git log --all --format='%ae' | sort -u
    # 期望：仅 17855593657@163.com 与 infinity@infinitys-MacBook-Pro.local

# ============ 验收 #5：GitHub 仓库可访问（推送后执行）============
curl -s -o /dev/null -w "repo=%{http_code}\n" https://github.com/KIDinfinity/workpilot          # 期望 200
curl -s -o /dev/null -w "readme=%{http_code}\n" https://raw.githubusercontent.com/KIDinfinity/workpilot/main/README.md   # 期望 200
curl -s -o /dev/null -w "license=%{http_code}\n" https://raw.githubusercontent.com/KIDinfinity/workpilot/main/LICENSE     # 期望 200
curl -sI https://raw.githubusercontent.com/KIDinfinity/workpilot/main/docs/assets/demo.gif | grep -i content-length
    # 期望：字节数 > 42（当前占位 42 字节 → P0 待替换真实录屏）
git ls-remote --tags https://github.com/KIDinfinity/workpilot.git    # 期望：含 v0.0.0 及全部 tag

# ============ 验收 #6：简历 ≥ 3 条带数字 bullet ============
grep -c '^- ' ~/lab/projects/career/resume/ai-fullstack-draft.md    # 期望 ≥ 3（当前 4）

# ============ 验收 #7：10 道 RAG 面试题 ============
grep -c '^### Q' ~/lab/projects/career/interview-questions.md        # 期望 ≥ 10（当前 10）

# ============ 验收 #8：能力矩阵 ≥ 12 项有模块证明 ============
grep -c '| M[0-9]' ~/lab/projects/career/capability-matrix.md        # 期望 ≥ 12（当前 17）

# ============ 补充：部署服务器在线验证（basic_auth）============
curl -s -o /dev/null -w "health=%{http_code}\n" http://8.148.216.61/health
    # 期望 401（basic_auth 生效 = 服务在线，非 000/超时即说明 Caddy 在监听 80）
```

---

## 五、待用户操作清单（按优先级）

1. **决策并修复 `/Users/` 路径泄露**（P0-1）：改 eval 报告写相对路径 + `git filter-repo` 重写历史（须用户确认）。
2. **替换 demo.gif**（P0-2）：录制真实演示录屏覆盖 `docs/assets/demo.gif`。
3. **填写敏感词表**（P1-1）：编辑 `~/lab/.private/sensitive-words.txt`，再重跑验收 #2 的敏感词 grep。
4. **确认 MIT 版权人**（P1-2）：`infinity` 或 `KIDinfinity`。
5. **提交并推送**（用户执行）：`workpilot` → `github.com/KIDinfinity/workpilot`（含 LICENSE + 全部 tag）；`projects` 仓库提交（验收 #8）。

以上完成后，8 项验收可全部勾选，Task 3 → DONE，进入 Day33。
