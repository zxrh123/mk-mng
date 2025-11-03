import type { ReactNode } from "react";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Gauge, Server } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

import { useNetworkStore } from "@/store/useNetworkStore";

const cardMotion = {
  hidden: { y: 20, opacity: 0 },
  visible: (i: number) => ({ y: 0, opacity: 1, transition: { delay: i * 0.1 } }),
};

export const MetricGrid = () => {
  const { snapshot, history, anomalies, loading, startAutoRefresh } = useNetworkStore();

  useEffect(() => startAutoRefresh(), [startAutoRefresh]);

  const latest = snapshot?.metrics;

  const chartData = history.map((item) => ({
    time: new Date(item.metrics.updated_at).toLocaleTimeString(),
    cpu: item.metrics.cpu_load,
    memory: item.metrics.memory_usage,
    latency: item.metrics.latency_ms,
  }));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={<Activity className="h-5 w-5 text-brand" />}
          title="CPU Load"
          value={latest ? `${latest.cpu_load.toFixed(1)}%` : "--"}
          trend="????? ??? ?????"
          index={0}
        />
        <MetricCard
          icon={<Gauge className="h-5 w-5 text-brand" />}
          title="Memory Usage"
          value={latest ? `${latest.memory_usage.toFixed(1)}%` : "--"}
          trend="?????? ??????"
          index={1}
        />
        <MetricCard
          icon={<Server className="h-5 w-5 text-brand" />}
          title="Latency"
          value={latest ? `${latest.latency_ms.toFixed(2)} ms` : "--"}
          trend="????? ?????? ping"
          index={2}
        />
        <MetricCard
          icon={<Server className="h-5 w-5 text-brand" />}
          title="Packet Loss"
          value={latest ? `${latest.packet_loss.toFixed(2)}%` : "--"}
          trend="????? ?????"
          index={3}
        />
      </div>

      <motion.div
        className="rounded-3xl border border-white/10 bg-white/5 p-6"
        initial="hidden"
        animate="visible"
        variants={cardMotion}
        custom={4}
      >
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="font-heading text-xl text-white">???? ?????? ??????</h2>
            <p className="text-xs text-white/50">CPU / Memory / Latency</p>
          </div>
          {loading && <span className="animate-pulse-soft text-xs text-brand">???? ???????...</span>}
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ left: -10, right: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#94a3b8" tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(3,7,18,0.9)",
                  borderRadius: 12,
                  border: "1px solid rgba(148,163,184,0.2)",
                  color: "white",
                }}
              />
              <Line type="monotone" dataKey="cpu" stroke="#0ea5e9" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory" stroke="#6366f1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="latency" stroke="#f472b6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {anomalies.length > 0 && (
        <motion.div
          className="rounded-3xl border border-magenta-500/30 bg-magenta-500/10 p-6"
          initial="hidden"
          animate="visible"
          variants={cardMotion}
          custom={5}
        >
          <h3 className="font-heading text-lg text-brand-magenta">??????? ????</h3>
          <ul className="mt-4 space-y-2 text-sm text-white/80">
            {anomalies.map((anomaly, idx) => (
              <li key={idx} className="rounded-xl bg-black/20 px-4 py-3">
                {JSON.stringify(anomaly)}
              </li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
};

const MetricCard = ({
  icon,
  title,
  value,
  trend,
  index,
}: {
  icon: ReactNode;
  title: string;
  value: string;
  trend: string;
  index: number;
}) => (
  <motion.div
    className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg"
    initial="hidden"
    animate="visible"
    variants={cardMotion}
    custom={index}
  >
    <div className="flex items-center justify-between">
      <span className="rounded-full bg-brand/10 p-3">{icon}</span>
      <span className="text-xs uppercase tracking-widest text-white/50">{trend}</span>
    </div>
    <div className="mt-6 space-y-2">
      <p className="text-sm text-white/50">{title}</p>
      <p className="text-2xl font-semibold text-white">{value}</p>
    </div>
  </motion.div>
);


