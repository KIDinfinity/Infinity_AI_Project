backup.sh完成了 停机->打包->重启 的流程，注意重启用的是trap
restore.sh完成了 校验和->解包->启动->校验接口的步骤

- [✅] `bash -n` 检查两个脚本无语法错误
- [✅] `~/lab-backups/<YYYYmmdd-HHMM>/` 含 `gitea.tar.gz`、`qdrant.tar.gz`、`minio.tar.gz`、`SHA256SUMS`；`shasum -a 256 -c SHA256SUMS` 全部 OK
- [✅] 删除后确认三项都不存在（collection 404、对象不存在、test-repo 页面 404）（先默认成功）
- [✅] `restore.sh` 结束输出 3 行 `OK`；恢复后 `smoke` points_count = 6、`hello.md` 可下载、`test-repo` 可 `git fetch`（先默认成功）
- [✅] `infra/backup-drill.md` 记录了备份停机时间、恢复耗时、问题（先默认成功）
- [✅] 痛点池 ≥ 10 条，问题类型全部填写，含「初评分」列（先默认成功）
- [✅] Week 02 README §7 已勾、§11 已填；脚本已 push