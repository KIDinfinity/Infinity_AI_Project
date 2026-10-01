# Week 23 · Portfolio 网站 + 在线 Demo（Phase 3 · Day70–Day71 · 12-06 → 12-07）

## 1. 本周核心目标

用 Astro 搭建静态 Portfolio 网站（首页 + P1/P2/P3 统一 9 段结构项目页 + Writing + About/简历下载），免费部署到 GitHub Pages（或 Cloudflare Pages）；为 WorkPilot v2.0 开放安全的在线 Demo（viewer 演示账号 + 公开语料 demo 空间 + 低预算守卫 + 每晚重置），录制 3 段演示视频嵌入网站，并完成发布前安全检查（gitleaks、Demo 无写权限、无公司数据）。

## 2. 资产锚点

| 构建模块                                                                            | 版本里程碑       | 本周结束 WorkPilot 能演示什么                                                                                                                    |
| ----------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| M13.5 Portfolio 网站、M12.4 在线 Demo、M12.3 产品页（与作品集共用）、M13.2 项目写作 | v2.0（对外发布） | 一个公开 URL：3 个项目页统一结构、3 段视频、Demo 入口；陌生人可用演示账号登录 WorkPilot，在 demo 空间问答并 dry-run 需求拆解，无法写任何外部系统 |

## 3. 为什么这一周存在

- 总计划 §6.4：Portfolio 统一展示 3 个项目（Problem → Why AI → Architecture → Implementation → Evaluation → Badcases → Optimization → Deployment → Result）。
- 招聘方平均只看几十秒：一个链接 + 视频 + 可点的 Demo 比 README 更有效。
- 对外开放前必须安全检查（蓝图 §8 第 5 条：W23 发布前敏感信息检查）。

## 4. 本周在路线中的位置

```text
上周产出（W22）：v2.0.0、Eval v2 报告、personal-ai-engineering、Pro Kit
        ↓
本周（W23）：Astro Portfolio（p1/p2/p3 来自 docs/portfolio/）→ Pages 部署
             demo 空间 + viewer 账号 + dry-run + 预算/限流 + 夜间重置 → 3 段视频 → gitleaks / 发布前检查清单
        ↓
下周输入（W24）：简历中的 Portfolio / Demo / GitHub 链接；facts.md 引用的报告链接
```

## 5. 每日安排

| Day   | 日期  | Task                                          | 当日 P0 产出                                                      | 模块  | 状态 |
| ----- | ----- | --------------------------------------------- | ----------------------------------------------------------------- | ----- | ---- |
| Day70 | 12-06 | Task 1：Portfolio 网站                        | Astro 站点 4 类页面 + p1/p2/p3 9 段结构 + Pages 上线              | M13.5 | TODO |
| Day71 | 12-07 | Task 2：在线 Demo + 演示视频 + 发布前安全检查 | demo 账号/空间/重置 + 安全检查清单全绿 + 至少 1 段视频（3 段 P1） | M12.4 | TODO |

## 6. 本周必须留下的资产

- `~/lab/portfolio/`（Gitea 仓库 + GitHub 镜像，Astro 项目）
- `portfolio/src/content/projects/{p1,p2,p3}.md`、`src/pages/{index,writing,about}.astro`
- `portfolio/.github/workflows/deploy.yml`（GitHub Pages）
- WorkPilot：`apps/api/app/cli.py`（`reset-demo` 命令）、`data/sample/demo/`（公开语料）、`deploy/cron/reset-demo`
- `docs/security/release-checklist.md`（发布前检查记录）
- 视频：`p1-90s.mp4`、`p2-2min.mp4`、`p3-2min.mp4`（压缩后，或外部视频平台链接）
- 公开 URL：Portfolio、Demo

## 7. 本周验收标准

- [ ] PASS / FAIL：Portfolio 公网可访问，首页 3 张项目卡片 + 一句话定位
- [ ] PASS / FAIL：3 个项目页结构一致（9 段），每页至少 1 个指向 Eval 报告的数字
- [ ] PASS / FAIL：About 页可下载简历（W24 前可放 v1，W24 替换）
- [ ] PASS / FAIL：演示账号可登录；只能看到 demo 空间；SP-B 只能 dry-run；写工具 0 次成功
- [ ] PASS / FAIL：demo 空间每晚自动重置（cron 日志可证）；demo 空间日预算 ≤ ¥2，超出降级/拒绝
- [ ] PASS / FAIL：gitleaks 扫 workpilot / personal-ai-engineering / portfolio 三个公开仓库无发现
- [ ] PASS / FAIL：发布前检查清单逐项勾选（无公司名、无内部链接、无真实数据）
- [ ] PASS / FAIL：3 段视频已嵌入（至少 P3 一段为 P0）

## 8. 求职映射

- 本周能力：技术写作、作品集叙事、静态站点部署、公开 Demo 的安全运营。
- 简历 bullet 草稿：「建设个人 AI 工程作品集（Astro + GitHub Pages），3 个项目统一 Problem → Result 叙事，配在线 Demo 与演示视频」
- 面试题：
  1. 3 分钟介绍你最好的项目。（答要点：按网站 9 段结构压缩：问题 / 为什么 AI / 架构 / 难点 / 评测数字 / badcase 与优化 / 部署 / 结果）
  2. 公开 Demo 如何防滥用？（答要点：只读角色、dry-run、独立空间、日预算、限流、夜间重置、无真实数据）

## 9. 本周禁止事项

- 不加 WorkPilot 产品功能（只加 demo 运营所需的最小改动）。
- 不购买付费主题、付费托管、付费视频平台。
- 不在网站、视频、Demo 中出现公司名、同事、内部系统、真实业务数据。
- 不做博客系统、评论系统、多语言站点。

## 10. 时间不够时（最小保留）

- Day70：首页 + 3 个项目页（内容可先粗）+ 部署上线；Writing 页可只放链接列表。
- Day71：demo 账号 + dry-run + 安全检查清单 + P3 一段视频；另两段视频在 W24 碎片时间补。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：公开 Portfolio + 公开 Demo）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
