# Day 71 · 2026-12-07 · Week 23 Task 2：在线 Demo + 演示视频 + 发布前安全检查

## 0. 今天只做一件事

让陌生人能安全地试用 WorkPilot v2.0（viewer 演示账号 + 公开语料 demo 空间 + dry-run + 低预算 + 每晚重置），完成所有公开仓库与 Demo 的发布前安全检查，并录制演示视频嵌入 Portfolio。

不碰：新功能（只加 demo 运营所需最小改动）、付费视频平台、正式上架 Pro Kit 收款（检查通过后另行决定）。

## 1. 资产锚点

- 构建模块：M12.4 在线 Demo、M11 安全（demo 运营与发布检查）、M13.2 项目写作（视频）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v2.0（对外发布）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：Portfolio 上的 Demo 入口 + 演示账号，任何人可体验问答与需求拆解 dry-run；`release-checklist.md` 全绿；3 段视频
- 今日 AI 实际应用：把 W15 预算守卫、W19 RBAC、W21 工具策略组合成「公开环境下的 AI 滥用防护」

## 2. 起点（前置确认）

- 已有：v2.0 线上；Workspace 表有 `is_demo` 字段（Day59 设计）；W15 日预算守卫；W21 policy；Day70 Portfolio。
- 需确认：

```bash
cd ~/lab/workpilot
grep -n "is_demo" apps/api/app/db/models.py               # 字段存在
grep -n "daily_budget\|budget" apps/api/app/obs/*.py | head   # 预算守卫按空间配置的方式
ls data/sample/                                              # 公开语料（W4 起使用的开源文档）
ssh deploy@<server> 'crontab -l 2>/dev/null | head'          # 现有 cron（备份）
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `uv run python -m app.cli reset-demo` 幂等执行：清空并重建 demo 空间、导入公开语料、确保演示账号存在（viewer）
- [ ] 演示账号登录后只看到 demo 空间；可 KB 问答、看历史运行；可 dry-run SP-B（停在草案，批准按钮禁用并提示）
- [ ] demo 空间：日预算 ≤ ¥2（超出返回友好提示）、限流比普通空间更严（如 10 次 / 小时 / 用户）
- [ ] demo 空间写工具全部被策略拒绝；即使误配置，Gitea 目标也只是沙盒仓库
- [ ] 服务器 cron 每晚 03:00 执行 reset-demo，日志可见
- [ ] gitleaks 扫描 workpilot / personal-ai-engineering / portfolio 无发现
- [ ] `docs/security/release-checklist.md` 全部勾选
- [ ] 视频：P3 2min（P0），P1 90s、P2 2min（P1），已嵌入 Portfolio

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                             |
| ----------- | ------ | ------------------------------------------------ |
| 0–25 min    | P0     | `reset-demo` CLI + 演示账号 + 公开语料导入       |
| 25–40 min   | P0     | dry-run 模式 + demo 预算 / 限流配置              |
| 40–50 min   | P0     | 服务器 cron + 首次执行验证                       |
| 50–70 min   | P0     | 发布前检查清单 + gitleaks × 3                    |
| 70–85 min   | P0     | 录制 P3 视频（2min）+ 压缩 + 嵌入                |
| 85–115 min  | P1     | 录制 P1 / P2 视频 + 嵌入；Portfolio 加 Demo 入口 |
| 115–120 min | P0     | 提交 + 部署                                      |
| 顺延        | P2     | Demo 使用统计面板、字幕、英文配音 → Backlog      |

时间不足时最低保留：demo 账号 + dry-run + 检查清单 + P3 视频。

## 5. 今日学习（只学完成任务必须的）

- **公开 Demo 的威胁**：成本滥用（刷 LLM）、数据污染（上传恶意文档）、越权写（建 issue）、把 Demo 当免费 API。对策：只读角色、独立空间、日预算、限流、定期重置、无真实数据。
- **dry-run**：执行到审批前并展示结果，但不允许进入写节点——用角色 + 空间标记在 API 层判断，而不是在前端隐藏按钮。
- **发布前检查**：秘密扫描（代码 + 历史）、内容审查（公司名 / 内部链接 / 真实数据）、权限审查（演示账号能做什么）。
- **视频叙事**：开头 10 秒说清「解决什么问题」，中间演示 1 条主路径，结尾 1 个数字 + 链接。
- 资料：https://github.com/gitleaks/gitleaks 、https://crontab.guru/

## 6. 执行步骤

### Step 1 · reset-demo CLI（P0，核心逻辑自己写）

```python
# app/cli.py（新增子命令；argparse/typer 以已有 create-owner 为准）
DEMO_WS_NAME = "demo"
DEMO_EMAIL = "demo@workpilot.example"

def reset_demo():
    with session_scope() as s:
        ws = s.exec(select(Workspace).where(Workspace.name == DEMO_WS_NAME)).first()
        if ws is None:
            ws = Workspace(name=DEMO_WS_NAME, is_demo=True); s.add(ws); s.flush()
        # 1) 清空 demo 空间业务数据（只删 workspace_id == ws.id）
        for model in (Feedback, Message, Conversation, AgentStep, Approval, AgentRun, KBDocument, Job):
            s.exec(delete(model).where(model.workspace_id == ws.id))
        vector_store.delete_by_workspace(str(ws.id))          # Qdrant 按 payload 过滤删除
        # 2) 演示账号（viewer），密码来自环境变量 DEMO_PASSWORD
        user = ensure_user(s, DEMO_EMAIL, os.environ["DEMO_PASSWORD"])
        ensure_membership(s, user.id, ws.id, role="viewer")
        # 3) 入队导入公开语料
        for path in sorted(Path("data/sample/demo").glob("*.md")):
            enqueue_ingest(s, ws.id, path)
    print("demo reset ok")
```

`data/sample/demo/`：只放开源许可允许再分发的文档（如开源项目文档、自己写的规范示例），在 README 中注明来源与许可证。审计日志不删除（保留滥用证据）。

### Step 2 · dry-run + 预算 / 限流（P0）

- 启动 SP-B：Day62 规则是 viewer → 403。改为：`ctx.role == "viewer" and workspace.is_demo` → 允许启动，state 写入 `dry_run=True`；`route_after_review` 中 `dry_run` 直接去 `summary`；resume 接口对 dry_run 运行返回 403「Demo 模式不执行写入」。
- 前端：dry_run 运行显示横幅「Demo 模式：可查看草案，无法创建 Issue」，批准按钮 disabled。
- 预算：W15 预算守卫支持按空间配置 → demo 空间 `daily_budget_cny=2`；超出返回 429 + 「今日演示额度已用完，请明天再试或观看视频」。
- 限流：slowapi key 改为 `user_id`，demo 空间 `10/hour`。
- 工具：W21 `ROLE_CAN_WRITE["viewer"] = False` 已保证写工具拒绝；再确认 demo 环境 Gitea token 只对沙盒仓库有写权限（双保险）。

### Step 3 · 服务器 cron（P0）

```bash
# deploy/cron/reset-demo（提交到仓库，服务器上安装）
0 3 * * * cd /opt/workpilot && docker compose --env-file .env.deploy -f docker-compose.prod.yml exec -T api python -m app.cli reset-demo >> /var/log/workpilot-reset-demo.log 2>&1
```

```bash
ssh deploy@<server> 'crontab -l > /tmp/c; cat /opt/workpilot/cron/reset-demo >> /tmp/c; crontab /tmp/c; crontab -l | tail -2'
ssh deploy@<server> 'cd /opt/workpilot && docker compose --env-file .env.deploy -f docker-compose.prod.yml exec -T api python -m app.cli reset-demo'
```

> 服务器时区确认为 Asia/Shanghai，或按 UTC 换算。日志文件需 deploy 用户有写权限。

### Step 4 · 发布前检查清单（P0）

`docs/security/release-checklist.md`：

```markdown
# 发布前检查 · v2.0 公开发布（2026-12-07）

## 秘密

- [ ] gitleaks：workpilot（含历史）无发现
- [ ] gitleaks：personal-ai-engineering 无发现
- [ ] gitleaks：portfolio 无发现
- [ ] .env / .env.deploy 不在任何仓库；`git log --all -- '*.env'` 为空

## 内容

- [ ] 全文搜索公司名 / 产品名 / 同事姓名 / 内部域名：0 命中（关键词清单只在本地，不提交）
- [ ] eval/datasets 与 badcases 仅含脱敏或公开内容
- [ ] 视频与截图无公司信息、无真实账号、无浏览器书签栏泄露

## Demo 权限

- [ ] 演示账号角色 = viewer，仅属于 demo 空间
- [ ] 尝试 resume / 上传 / 成员管理 → 403
- [ ] demo 日预算与限流生效（手动触发一次 429）
- [ ] Gitea token 仅对沙盒仓库有写权限

## 运维

- [ ] 最近一次备份时间：\_**\_；恢复演练记录：\_\_**
```

```bash
for r in workpilot personal-ai-engineering portfolio; do
  echo "== $r"; docker run --rm -v "$HOME/lab/$r:/repo" ghcr.io/gitleaks/gitleaks:latest git /repo -v --redact | tail -5
done
# 内容关键词检查（关键词清单保存在 ~/lab/private/sensitive-words.txt，不入库）
for r in workpilot personal-ai-engineering portfolio; do grep -rniF -f ~/lab/private/sensitive-words.txt ~/lab/$r --exclude-dir=node_modules --exclude-dir=.git; done
```

> 若 gitleaks 在历史中发现真实密钥：**先在服务端吊销/轮换该密钥**，再评估是否重写历史；重写已推送的历史属于破坏性操作，执行前单独确认。

### Step 5 · 视频（P0 / P1）

| 视频     | 时长  | 主路径                                                                 | 结尾数字                     |
| -------- | ----- | ---------------------------------------------------------------------- | ---------------------------- |
| P3（P0） | 2 min | 登录 → 粘贴需求 → 时间线 → 编辑任务表 → 批准 → Issue 链接 → 评测趋势页 | rubric 通过率、攻击拦截 100% |
| P1       | 90 s  | 上传文档 → 带引用回答 → 点击引用 → 库外问题拒答                        | hit@5、引用正确率            |
| P2       | 2 min | Research Agent 时间线 → 写工具审批 → VS Code 中通过 MCP 调用 kb_ask    | 任务成功率、工具选择准确率   |

录制：macOS `Cmd+Shift+5`，录制前切换干净浏览器 Profile、关闭通知；压缩：

```bash
ffmpeg -i p3-raw.mov -vf "scale=1280:-2" -c:v libx264 -crf 28 -preset slow -an p3-2min.mp4   # 无配音时 -an
```

放入 `portfolio/public/videos/`（单文件建议 < 20MB），项目页 Result 段前加 `<video controls preload="metadata" src={`${import.meta.env.BASE_URL}/videos/p3-2min.mp4`}></video>`；或上传视频平台后嵌入链接。Portfolio 首页 / P3 页加「在线 Demo」按钮 + 演示账号（公开只读账号，可直接写出）。

### Step 6 · 提交 + 部署

```bash
cd ~/lab/workpilot
git add apps/api apps/web/src deploy/cron docs/security/release-checklist.md data/sample/demo
git commit -m "feat(demo): read-only demo workspace with dry-run, budget, nightly reset" && git push
git tag -a v2.0.1 -m "v2.0.1: public demo hardening" && git push origin v2.0.1
cd ~/lab/portfolio && git add . && git commit -m "feat: demo entry and project videos" && git push && git push github main
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 dry-run 判断放在 API 层而不是前端隐藏按钮？（答：前端可被绕过，直接调 resume 接口；权限必须在服务端强制）
2. demo 重置为什么不删 AuditLog？（答：审计日志用于追溯滥用，重置只清业务数据）
3. 公开 Demo 最大的成本风险是什么，怎么控？（答：被刷 LLM 调用；按空间日预算 + 按用户限流 + 超额友好拒绝）
4. gitleaks 为什么要扫 git 历史而不只是当前文件？（答：删除的密钥仍在历史提交中，公开仓库可被任何人检出）
5. 发现历史泄露密钥第一步做什么？（答：立即吊销/轮换密钥；重写历史只是补救，且需要谨慎确认）

## 8. 对 DA-01 的贡献

WorkPilot 从「自己能演示」变成「任何人可安全试用」：Demo 是作品集最强证据，也是 Pro Kit 潜在用户的试用入口（蓝图 §10「有人下载/试用」的验证渠道）。发布前检查让公开发布符合数据合规红线。

## 9. 求职映射（D 线）

- 岗位能力：公开环境安全运营、成本控制、发布流程、产品演示能力。
- 对应岗位：AI Full-Stack Engineer、AI Platform Engineer。
- 简历 bullet 草稿：「上线公开只读 Demo（viewer 角色 + dry-run + 空间日预算 ¥2 + 限流 + 夜间重置），发布前完成秘密扫描与内容合规检查」
- 面试可能问：
  1. 如何安全地开放一个 LLM 应用给公众试用？——要点：最小权限账号、隔离数据、预算与限流、无写操作、可重置、监控与审计。
  2. 演示中出现失败怎么办？——要点：准备视频兜底；Demo 预置稳定样例；如实说明局限与评测数据。

## 10. 卡住时的处理

| 现象                                       | 处理                                                                                           |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| Qdrant 按空间删除不生效                    | 用 `client.delete(collection, points_selector=models.FilterSelector(filter=<workspace 过滤>))` |
| cron 中 `docker compose exec` 报 not a TTY | 必须加 `-T`                                                                                    |
| 演示账号能看到 personal 空间               | Membership 多了一条：reset-demo 只确保 demo 成员关系，手动删除多余 membership 并加测试         |
| 视频文件过大推送失败                       | 提高 `-crf`（如 30）或降到 960 宽；或改用视频平台链接                                          |
| gitleaks 命令报 unknown command            | 旧版本用 `detect --source /repo -v`；新版本 `git` / `dir` 子命令                               |
| 时间不够                                   | 视频只录 P3；P1/P2 复用 W8/W16 已有录屏                                                        |

## 11. 产出记录（执行时填写）

- Demo URL / 演示账号：\_\_\_\_ / demo@workpilot.example
- 写操作尝试结果：resume ** / 上传 ** / 成员管理 \_\_（均应 403）
- 预算 429 触发验证：是 / 否
- gitleaks：workpilot ** / pae ** / portfolio \_\_
- 视频：P3 ** s（** MB）/ P1 ** / P2 **
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day72 · W24 Task 1「三版简历」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（demo 权限 + 检查清单 + P3 视频）；检查清单未全绿前不得在简历中放 Demo 链接。
