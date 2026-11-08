import { DemoCard } from "./DemoCard";
import { ChatDemo } from "../demos/ChatDemo";
import { CodeDemo } from "../demos/CodeDemo";
import { SummaryDemo } from "../demos/SummaryDemo";

export function DemoSection() {
  return (
    <section className="mx-auto max-w-2xl px-4 py-12">
      <h2 className="mb-6 text-center text-2xl font-bold">AI 能力演示</h2>
      <div className="space-y-6">
        <DemoCard
          title="智能问答"
          description="问我关于技术栈的问题，AI 从预设知识回答"
          tags={["Streaming", "System Prompt", "Token 限制"]}
        >
          <ChatDemo />
        </DemoCard>
        <DemoCard
          title="代码解释 / 转换"
          description="贴一段代码，AI 解释它或转成其他语言"
          tags={["Structured Output", "JSON"]}
        >
          <CodeDemo />
        </DemoCard>
        <DemoCard
          title="文档摘要"
          description="贴一段长文本，AI 生成摘要和关键词"
          tags={["长文本截断", "JSON"]}
        >
          <SummaryDemo />
        </DemoCard>
      </div>
    </section>
  );
}
