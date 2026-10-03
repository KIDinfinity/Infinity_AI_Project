[✅] Gitea 上存在 Private 仓库 ai-project-template，本地在 ~/lab/ai-project-template
[✅] find . -path ./.git -prune -o -print | sort 输出与本计划 Step 2「预期输出」一致
[✅] git check-ignore -v .env .env.local data/x.csv eval/runs/a.json 4 行均有输出
[✅] git check-ignore .env.example data/README.md data/sample/README.md 无输出（echo $? 为 1）
[✅] PROJECT_STANDARD.md 含 9 节（grep -c '^## ' PROJECT_STANDARD.md ≥ 9）
[✅] 合上文档，口述 8 个顶层目录（apps / prompts / eval / data / deploy / scripts / docs / .gitea）各放什么、不放什么
[✅] git log --oneline origin/main 有今天的提交