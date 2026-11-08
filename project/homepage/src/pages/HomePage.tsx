import { Hero } from "../components/Hero";
import { About } from "../components/About";
import { DemoSection } from "../components/DemoSection";
import { NewsFeed } from "../components/NewsFeed";
import { ToolboxPreview } from "../components/ToolboxPreview";
import { Footer } from "../components/Footer";

export function HomePage() {
  return (
    <>
      <Hero />
      <About />
      <DemoSection />
      <NewsFeed />
      <ToolboxPreview />
      <Footer />
    </>
  );
}
