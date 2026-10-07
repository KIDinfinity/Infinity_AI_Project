# Week 07 · Docker 化 + 云部署 + CI + 备份（Phase 1 · Day26–Day29 · 11-09 → 11-12）

## 1. 本周核心目标

把 v0.4 从「只能在我 Mac 上 `make dev` 跑」变成**任何人拿到仓库都能一键起、公网可访问、每次推送自动检查、数据可备份可恢复**的工程化交付物。

一句话验收：**`make up` 本地一键起全栈；`https://<你的域名>` 带 basic auth 可问答；Gitea Actions CI 绿；云端备份 → 清空 → 恢复演练有耗时记录。**

## 2. 资产锚点

| 构建模块                                | 版本里程碑     | 本周结束 WorkPilot 能演示什么                                       |
| --------------------------------------- | -------------- | ------------------------------------------------------------------- |
| M5.1 Dockerfile + compose（dev / prod） | 为 v0.5 做准备 | `make up` → http://localhost:8080 全流程可用                        |
| M5.2 配置 / 健康检查 / JSON 日志        | 为 v0.5 做准备 | `/health` `/ready` JSON 明细；每行日志带 `request_id`；统一错误格式 |
| M9.1 request_id                         | 为 v0.5 做准备 | 响应头 `X-Request-ID`，前端报错可直接 grep 日志                     |
| M5.3 云部署 + HTTPS                     | 为 v0.5 做准备 | 公网 HTTPS 地址 + basic auth + SiliconFlow embedding                |
| M5.4 CI                                 | 为 v0.5 做准备 | push 后 Gitea Actions：ruff + pytest + tsc + build 全绿             |
| M5.5 备份 / 恢复 / 运行手册             | 为 v0.5 做准备 | `backup.sh` 每日 cron；恢复演练耗时写入 `docs/runbook.md`           |

## 3. 为什么这一周存在

- **「能部署」是 AI Engineer 与「调 API 写 Demo」的分水岭**：JD 中 Docker / Cloud / CI/CD / Observability 几乎必出现；面试官会问「你的项目怎么上线、怎么排障、挂了怎么恢复」。
- P1 验收要求「公网可访问」和「干净环境 30 分钟恢复」（phase_01 README §8），本周是这两条的唯一来源。
- request_id + JSON 日志是 W15 Trace / 成本看板的地基；compose 是 W19 Postgres 与自动部署的地基。

## 4. 本周在路线中的位置

```text
W6 产出：apps/web + apps/api（SQLite 会话 / 反馈 / 文档表）→ v0.4.0
   ↓
W7 本周：Dockerfile ×2 + Caddyfile + compose(dev/prod) + /health /ready + JSON 日志
         + 云服务器 HTTPS + basic auth + Gitea Actions CI + 备份恢复 runbook
   ↓
W8 输入：公网 Demo 地址、CI 徽章、runbook、可复现的 make up
         → README / 架构图 / Demo 录制 / GitHub 公开 / 干净环境恢复验收
```

## 5. 每日安排

| Day | 日期  | Task                                             | 当日 P0 产出                                   | 模块      | 状态 |
| --- | ----- | ------------------------------------------------ | ---------------------------------------------- | --------- | ---- |
| 26  | 11-09 | Task 1：Dockerfile + compose 全栈                | `make up` → localhost:8080 上传 + 问答通过     | M5.1      | TODO |
| 27  | 11-10 | Task 2：配置 / 健康检查 / JSON 日志 / request_id | `/ready` 明细 + 日志带 request_id + 统一错误体 | M5.2 M9.1 | TODO |
| 28  | 11-11 | Task 3：云部署 + HTTPS + 访问保护                | 公网 HTTPS + basic auth + 问答可用             | M5.3      | TODO |
| 29  | 11-12 | Task 4：CI + 云端备份恢复演练                    | CI 绿 + 恢复耗时记录 + 周复盘                  | M5.4 M5.5 | TODO |

## 6. 本周必须留下的资产（文件路径级）

```text
~/lab/workpilot/
├── .dockerignore                         # 仓库根（构建上下文 = 仓库根）
├── .env.example                          # 补齐所有新变量（无真实值）
├── Makefile                              # + up / down / logs / ps / seed / deploy
├── apps/api/Dockerfile                   # uv 多阶段，非 root
├── apps/api/app/core/{config.py,logging.py,middleware.py,errors.py}
├── apps/api/app/routes/health.py         # /health /ready
├── apps/web/Dockerfile                   # node 构建 → caddy 托管 dist
├── data/sample/*.md + SOURCES.md         # 公开样例语料（提交到 Git）
├── scripts/seed_sample.sh                # 批量上传样例
├── deploy/
│   ├── Caddyfile                         # dev：:80
│   ├── Caddyfile.prod                    # 域名 + 自动 HTTPS + basic_auth
│   ├── docker-compose.yml                # dev
│   ├── docker-compose.prod.yml           # prod：不暴露 qdrant/minio
│   └── scripts/{deploy.sh,backup.sh,restore.sh}
├── .gitea/workflows/ci.yml
└── docs/runbook.md                       # 部署 / 备份 / 恢复 / 排障 + 演练记录
```

## 7. 本周验收标准

- [ ] PASS / FAIL：`make down && make up` 后，http://localhost:8080 上传 + 流式问答 + 引用正常
- [ ] PASS / FAIL：api 镜像以非 root 运行（`docker compose exec api id` 非 uid 0）
- [ ] PASS / FAIL：缺少必填环境变量时 api 启动即失败并打印缺哪一项
- [ ] PASS / FAIL：`/ready` 在 Qdrant 停止时返回 503 且指明 qdrant 失败
- [ ] PASS / FAIL：日志为 JSON，同一请求的所有行 `request_id` 相同，且与响应头一致
- [ ] PASS / FAIL：500 响应体不含堆栈 / 密钥，格式为 `{"error":{"code","message","request_id"}}`
- [ ] PASS / FAIL：`https://<域名>` 证书有效；未带凭据返回 401；带凭据可问答
- [ ] PASS / FAIL：服务器 `ss -tlnp` 只有 22/80/443 对外；`.env` 权限 600
- [ ] PASS / FAIL：Gitea Actions CI 在 main 上为绿色
- [ ] PASS / FAIL：云端备份 → 清空卷 → 恢复 → 问答通过，耗时写入 runbook

## 8. 求职映射

- **本周能力**：Docker 多阶段构建、Compose 编排与健康检查、Caddy 反代 / 自动 HTTPS、Linux 服务器加固、结构化日志与请求追踪、CI、备份恢复（RTO 意识）。
- **简历 bullet 草稿**：
  - 使用 Docker 多阶段构建（uv）+ Compose 编排 API / Web / Qdrant / MinIO，配合 Caddy 自动 HTTPS 部署至云服务器，镜像体积 \_\_MB，`make up` 一键启动。
  - 实现 request_id 贯穿的 JSON 结构化日志、`/health` 与 `/ready` 分离的健康检查及统一错误响应，线上问题定位时间从 ** 分钟降至 ** 分钟。
  - 搭建 Gitea Actions CI（lint / test / typecheck / build）与每日备份脚本，完成一次全量恢复演练，RTO \_\_ 分钟。
- **面试题**：
  1. liveness 和 readiness 的区别？各自失败时编排系统做什么？
  2. 一个用户说「刚才报错了」，你怎么在日志里找到那次请求？（request_id 从前端 → 响应头 → 日志）
  3. 你的备份方案是什么？怎么证明它能用？（快照 + 异地 + 保留策略 + 定期恢复演练 + 记录 RTO）

## 9. 本周禁止事项

- 不上 Kubernetes / Swarm / Terraform / Ansible（单机 Compose 足够，DA01 Non-goals）。
- 不引入 Prometheus / Grafana / Loki / ELK（JSON 日志 + `docker compose logs` 足够，W15 再做轻量 trace）。
- 不做蓝绿 / 灰度发布、不做自动部署（W19 再做 push 即部署）。
- 不把公司数据、`data/corpus` 中的非公开内容传到云服务器（DA01 §8）。
- 不为省钱折腾多个云厂商比价超过 20 分钟；不买超过 2C4G 的机器。

## 10. 时间不够时（最小保留）

1. Day26 `make up` 本地全栈可用（W8 干净环境恢复的前提）
2. Day28 公网 HTTPS + basic auth（P1 验收「公网可访问」）
3. Day27 至少做 `/health` + request_id 响应头 + 统一错误体（JSON 日志可简化）
4. Day29 CI 与云端恢复演练可 CONDITIONAL，在 W9 第一天补齐（phase_01 README §8 允许）

## 11. 周复盘（Day29 末尾填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（公网地址、CI 截图、恢复耗时）
- 是否出现无效学习或范围扩张（例如研究 K8s、折腾监控栈）：\_\_\_\_
- 本周实际云 / 域名花费：¥\_\_\_\_
- 下周调整：\_\_\_\_
