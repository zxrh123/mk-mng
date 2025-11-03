import { useMemo } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { TelemetryHistoryPoint } from "../hooks/useTelemetry";
import { strings } from "../lib/strings";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";

interface TelemetryChartsProps {
  host: string;
  data?: TelemetryHistoryPoint[];
}

export const TelemetryCharts = ({ host, data = [] }: TelemetryChartsProps) => {
  const formatted = useMemo(
    () =>
      data.map((point) => ({
        time: new Date(point.recorded_at).toLocaleTimeString("ar-EG", { hour: "2-digit", minute: "2-digit" }),
        cpu: Number((point.cpu_load * 100).toFixed(2)),
        memory: Number((point.memory_usage * 100).toFixed(2)),
        latency: Number(point.latency_ms.toFixed(2)),
        loss: Number((point.packet_loss * 100).toFixed(2))
      })),
    [data]
  );

  return (
    <Card className="col-span-2">
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-lg font-bold text-white">{strings.telemetry.chartTitle} {host}</CardTitle>
          <span className="text-sm text-azure/70">{strings.telemetry.refresh}</span>
      </CardHeader>
      <CardContent className="grid gap-8 md:grid-cols-2">
        <div className="h-64">
          <ResponsiveContainer>
            <AreaChart data={formatted} syncId="telemetry">
              <defs>
                <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="10%" stopColor="#1be7ff" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#1be7ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="time" stroke="#b8e1ff" />
              <YAxis unit="%" stroke="#b8e1ff" domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "rgba(7,20,40,0.9)", borderRadius: 16, border: "1px solid #1be7ff" }} />
              <Area type="monotone" dataKey="cpu" stroke="#1be7ff" fill="url(#cpuGradient)" strokeWidth={2} />
              <Area type="monotone" dataKey="memory" stroke="#ff009e" fillOpacity={0.15} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="h-64">
          <ResponsiveContainer>
            <AreaChart data={formatted} syncId="telemetry">
              <defs>
                <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00a4ff" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#00a4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="time" stroke="#b8e1ff" />
              <YAxis stroke="#b8e1ff" />
              <Tooltip contentStyle={{ background: "rgba(7,20,40,0.9)", borderRadius: 16, border: "1px solid #00a4ff" }} />
              <Area type="monotone" dataKey="latency" stroke="#00a4ff" fill="url(#latencyGradient)" strokeWidth={2} />
              <Area type="monotone" dataKey="loss" stroke="#ff009e" fillOpacity={0.15} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};
