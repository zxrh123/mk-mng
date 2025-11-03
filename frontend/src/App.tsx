import { AIChatPanel } from "@/components/AIChatPanel";
import { HeroHeader } from "@/components/HeroHeader";
import { MetricGrid } from "@/components/MetricGrid";
import { PlanTimeline } from "@/components/PlanTimeline";

const App = () => {
  return (
    <div className="min-h-screen bg-brand-dark/95 pb-16">
      <div className="pointer-events-none fixed inset-0 bg-grid-glow" aria-hidden="true" />
      <main className="relative z-10 mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
        <HeroHeader />
        <section className="grid gap-6 lg:grid-cols-[1.9fr_1.1fr]">
          <div className="space-y-6">
            <MetricGrid />
            <PlanTimeline />
          </div>
          <AIChatPanel />
        </section>
      </main>
    </div>
  );
};

export default App;
