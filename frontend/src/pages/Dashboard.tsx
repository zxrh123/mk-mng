import { useMemo, useState } from "react";
import { FlameKindling, Radar, Wifi, Activity, Server } from "lucide-react";

import { AIStatusIndicator } from "../components/AIStatusIndicator";
import { ChatWidget } from "../components/ChatWidget";
import { DashboardCard } from "../components/DashboardCard";
import { NotificationCenter } from "../components/NotificationCenter";
import { TelemetryCharts } from "../components/TelemetryCharts";
import { Button } from "../components/ui/Button";
import { useLatestTelemetry, useTelemetryHistory } from "../hooks/useTelemetry";
import { strings } from "../lib/strings";

const DEFAULT_HOST = "10.0.0.1";

export const Dashboard = () => {
  const [selectedHost, setSelectedHost] = useState(DEFAULT_HOST);
  const { data: latestTelemetry, isFetching } = useLatestTelemetry(selectedHost);
  const { data: history } = useTelemetryHistory(selectedHost);

  const metrics = useMemo(() => {
    if (!latestTelemetry) return [];
    return [
      {
        title: strings.dashboard.cpu.title,
        metric: `${Math.round(latestTelemetry.cpu_load * 100)}%`,
        trend: latestTelemetry.cpu_load > 0.8 ? strings.dashboard.cpu.high : strings.dashboard.cpu.stable,
        icon: <FlameKindling className="h-6 w-6" />,
        footer: (
          <p className="text-sm text-azure/70">
            {strings.dashboard.lastUpdateLabel} {new Date(latestTelemetry.recorded_at).toLocaleTimeString("ar-EG")}
          </p>
        )
      },
      {
        title: strings.dashboard.memory.title,
        metric: `${Math.round(latestTelemetry.memory_usage * 100)}%`,
        trend: latestTelemetry.memory_usage > 0.75 ? strings.dashboard.memory.watch : strings.dashboard.memory.great,
        icon: <Radar className="h-6 w-6" />
      },
      {
        title: strings.dashboard.latency.title,
        metric: `${latestTelemetry.latency_ms.toFixed(1)}ms`,
        trend: latestTelemetry.latency_ms > 50 ? strings.dashboard.latency.needsWork : strings.dashboard.latency.fast,
        icon: <Wifi className="h-6 w-6" />
      }
    ];
  }, [latestTelemetry]);

  return (
    <div className="space-y-8">
      <section className="flex flex-wrap items-center justify-between gap-6 rounded-3xl border border-azure/30 bg-glass px-8 py-6 shadow-glow">
        <div>
          <h2 className="text-3xl font-bold text-white">{strings.dashboard.title}</h2>
          <p className="text-sm text-azure/70">{strings.dashboard.subtitle}</p>
        </div>
        <div className="flex items-center gap-4">
          <AIStatusIndicator isThinking={isFetching} />
          <Button variant="secondary" className="gap-2" onClick={() => setSelectedHost(DEFAULT_HOST)}>
            <Server className="h-4 w-4" /> {strings.dashboard.primaryDevice}
          </Button>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {metrics.map((metric) => (
          <DashboardCard key={metric.title} {...metric} />
        ))}
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        <TelemetryCharts host={selectedHost} data={history?.points} />
        <NotificationCenter telemetry={latestTelemetry} />
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-azure/30 bg-glass px-6 py-5 text-sm text-azure/80">
          <h3 className="mb-3 text-lg font-semibold text-white">{strings.dashboard.aiDecisionsTitle}</h3>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <Activity className="mt-1 h-5 w-5 text-neon" />
              <div>
                <p>{strings.dashboard.decisionOne}</p>
                <span className="text-xs text-azure/60">{strings.dashboard.decisionOneTime}</span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Activity className="mt-1 h-5 w-5 text-magenta" />
              <div>
                <p>{strings.dashboard.decisionTwo}</p>
                <span className="text-xs text-azure/60">{strings.dashboard.decisionTwoTime}</span>
              </div>
            </li>
          </ul>
        </div>
        <div className="rounded-3xl border border-magenta/30 bg-magenta/10 px-6 py-5 text-sm text-white">
          <h3 className="mb-3 text-lg font-semibold">{strings.dashboard.knowledgeTitle}</h3>
          <p className="text-azure/80">{strings.dashboard.knowledgeText}</p>
        </div>
      </section>

      <ChatWidget host={selectedHost} />
    </div>
  );
};
