import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

export interface TelemetryPayload {
  device: string;
  cpu_load: number;
  memory_usage: number;
  latency_ms: number;
  packet_loss: number;
  anomalies: Record<string, number>;
  recorded_at: string;
}

export interface TelemetryHistoryPoint {
  recorded_at: string;
  cpu_load: number;
  memory_usage: number;
  latency_ms: number;
  packet_loss: number;
}

export const useLatestTelemetry = (host?: string) =>
  useQuery({
    queryKey: ["telemetry", "latest", host],
    queryFn: async () => {
      const response = await api.get<TelemetryPayload>("/monitoring/latest", {
        params: host ? { host } : undefined
      });
      return response.data;
    },
    refetchInterval: 30_000
  });

export const useTelemetryHistory = (host: string) =>
  useQuery({
    queryKey: ["telemetry", "history", host],
    queryFn: async () => {
      const response = await api.get<{ device: string; points: TelemetryHistoryPoint[] }>(
        "/monitoring/history",
        {
          params: { host, limit: 50 }
        }
      );
      return response.data;
    },
    enabled: Boolean(host)
  });
