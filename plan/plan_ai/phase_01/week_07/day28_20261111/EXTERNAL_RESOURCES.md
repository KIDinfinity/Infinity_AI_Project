# Day 28 外部资源清单

本文只记录当前部署尚未提供、需要准备的外部资源及其用途。拿齐资源后，可按同目录的 [SUMMARY.md](./SUMMARY.md) 执行部署和验收。

## 尚未提供的资源

| 资源 | 当前状态 | 用途 | 需要准备的内容 |
|---|---|---|---|
| 云服务器 | 未提供 | 运行 WorkPilot 的 API、Web、Caddy、Qdrant 和 MinIO 服务 | Ubuntu 22.04/24.04，建议至少 2 vCPU、4 GB 内存；公网 IP；云防火墙放行 TCP 22、80、443（可选 UDP 443） |
| 域名 | 未提供 | 让 Caddy 自动申请并续期 HTTPS 证书，并作为用户访问入口 | 一个可管理 DNS 的域名；添加 `wp` 子域名 A 记录指向服务器公网 IP，例如 `wp.example.com` |
| SiliconFlow API Key | 未提供 | 生产环境调用 `BAAI/bge-m3` 生成文本向量，供知识库检索使用 | SiliconFlow 账号及 API Key；部署时填入 `.env.prod` 的 `EMBEDDING_API_KEY` |
| 服务器 SSH 登录信息 | 未提供 | 首次安装 Docker、创建部署用户并完成服务器初始化 | 云服务器公网 IP，以及首次管理登录方式（建议云厂商控制台或临时 root/管理员凭据）；初始化后改用专用密钥登录 |
| SSH 部署密钥 | 尚未生成/提供 | 让本机通过 `wp-prod` 别名安全地运行部署脚本 | 在部署本机生成 Ed25519 密钥对；公钥配置到服务器 `deploy` 用户，私钥留在本机 `~/.ssh/workpilot_ed25519` |
| ACME 联系邮箱 | 未提供 | Caddy 申请 HTTPS 证书时使用，供证书机构发送重要通知 | 一个可收信的邮箱，填入 `.env.prod` 的 `ACME_EMAIL` |
| Basic Auth 账号与新密码 | 未提供 | 给尚未接入正式登录系统的 Demo 加访问门槛 | 自定义用户名和强密码；生成 Caddy bcrypt 哈希后填入 `.env.prod` 的 `BASIC_AUTH_USER`、`BASIC_AUTH_HASH`。不要使用模板里的示例密码 |

## 可能可复用、但需部署者确认

| 资源 | 当前状态 | 用途 / 确认方式 |
|---|---|---|
| DeepSeek LLM API Key | 本次信息未确认是否可用 | WorkPilot 生成回答时调用的 LLM 凭据；若现有 dev Key 仍有效且允许生产使用，可填入 `.env.prod` 的 `DEEPSEEK_API_KEY`，否则需在 DeepSeek 平台创建或充值可用 Key |

## 不需要另外申请

- **MinIO 凭据**：`.env.prod` 已包含本地生成的独立强凭据；部署时由 Compose 配置使用。若该文件曾分享给他人，应重新生成。
- **HTTPS 证书**：不需要手动购买或上传证书；域名解析正确且服务器 80/443 可达后，Caddy 会自动申请和续期。

## 准备完成检查

开始部署前确认：

1. 已拿到服务器公网 IP，且域名 `wp.<你的域名>` 的 DNS A 记录解析到该 IP。
2. 云防火墙放行 22、80、443；服务器可通过 SSH 管理。
3. 已生成并配置部署 SSH 密钥，能以 `deploy` 用户登录。
4. `.env.prod` 中的 SiliconFlow Key、LLM Key、域名、邮箱和 Basic Auth 用户/哈希均已填妥；没有 `<...>` 占位符。
5. Basic Auth 密码已更换为个人强密码，且 `.env.prod` 不提交到版本库。
