# @venus/aurora 发布流程

## 正确步骤

### 1. 修改代码
在 `feature/xxx` 分支上修改源码。

### 2. 更新版本号
修改 `package.json` 中的 `version` 字段（如 `0.0.9` → `0.0.10`）。

### 3. 提交并推送
```bash
git add .
git commit -m "feat: xxx"
git push origin head
```

### 4. 创建 PR 合并到 main
在 Azure DevOps 创建 Pull Request，将 `feature/xxx` 合并到 `main`。

### 5. 打 tag 触发发布
PR 合并后，在最新 `main` commit 上打 `v*` tag：
```bash
git fetch origin
git checkout main
git pull origin main
git tag v0.0.10
git push origin v0.0.10
```

> **注意**：`main` 分支有保护不允许直接 push，如果打 tag 被拦截，切到 feature 分支操作：
> ```bash
> git checkout feature/xxx
> git reset --hard origin/main
> git tag v0.0.10
> git push origin v0.0.10
> ```

### 6. 等待 CI 发布
推送 tag 后 Azure Pipelines 自动触发构建和 `npm publish`。去 Pipelines 页面确认构建成功。

### 7. 使用方更新依赖
```bash
# 在使用该包的项目中
npm install @venus/aurora@^0.0.10
```

---

## v0.0.10 发布失败原因分析

### 现象
`v0.0.10` tag 触发的 CI 构建报错：
```
403 Forbidden - The feed 'fwd-ctc' already contains file 'aurora-0.0.10.tgz'
```

### 根因
**`package.json` 版本号与 tag 不匹配，且 tag 指向了错误的 commit。**

时间线回顾：

| 步骤 | 操作 | 问题 |
|------|------|------|
| 1 | 在 `antd.ts` 中添加 `fontFamily` | ✅ 代码改动正确 |
| 2 | 创建 PR 合并到 `main` | ✅ 合并成功（commit `c106383`） |
| 3 | 打 `v0.0.10` tag | ❌ tag 已存在于远程，指向旧代码 |
| 4 | 打 `v0.0.11` tag | ❌ tag 指向 `c106383`，但 `package.json` 版本仍是 `0.0.10` |
| 5 | CI 构建 | ❌ 产物版本号为 `0.0.10`，与 feed 中已有版本冲突 |

**核心问题**：`v0.0.11` tag 指向的 commit 中 `package.json` 版本号是 `0.0.10`，CI 构建出的包名是 `aurora-0.0.10.tgz`，而 feed 中 `0.0.10` 已存在（之前 `v0.0.10` tag 发布过），导致 403 冲突。

### 修复
1. 将 `package.json` 版本号改为 `0.0.11`
2. 创建 PR 合并版本号更新到 `main`
3. 删除旧的 `v0.0.11` tag：`git push origin :v0.0.11`
4. 在最新 `main` commit 上重新打 `v0.0.11` tag
5. CI 构建产物为 `aurora-0.0.11.tgz`，与 feed 无冲突，发布成功

### 教训
- **`package.json` 的 `version` 必须与 tag 版本号一致**
- **打 tag 前确认 `package.json` 版本号已更新且已合并到 `main`**
- **如果 tag 发布失败需要重试，必须先删除远程旧 tag，更新版本号后重新打**