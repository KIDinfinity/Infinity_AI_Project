找首批badcase（实际还是验收结构化流式输出）

[✅] POST /v1/ask 返回 {answer: StructuredAnswer, source_note: "来源：模型通用知识（未接入知识库）", prompt, usage, cost, latency_ms}
[✅] POST /v1/ask/stream 用 curl -N 可见 token 流，done 事件含 source_note
[✅] eval/datasets/smoke_v0.jsonl 10 行，可被 json.loads 逐行解析
[✅] eval/reports/20261015-smoke-v0.1.md 存在：10 行结果 + 平均延迟 + 总成本 + low 置信占比
[✅] eval/badcases/badcases.md ≥ 3 条幻觉案例
[✅] README 有 v0.1 章节；git tag 有 v0.1.0 并已 push
[✅] Week 3 README 第 11 节已填写