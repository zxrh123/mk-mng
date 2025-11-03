import { create } from "zustand";
import { apiClient } from "@/lib/api";
import type { RouterSnapshot } from "@/types";

type NetworkState = {
  snapshot: RouterSnapshot | null;
  history: RouterSnapshot[];
  anomalies: Record<string, unknown>[];
  loading: boolean;
  error: string | null;
  fetchSnapshot: () => Promise<void>;
  startAutoRefresh: () => () => void;
};

export const useNetworkStore = create<NetworkState>((set, get) => ({
  snapshot: null,
  history: [],
  anomalies: [],
  loading: false,
  error: null,
  fetchSnapshot: async () => {
    try {
      set({ loading: true, error: null });
      const [snapshotRes, anomaliesRes] = await Promise.all([
        apiClient.get<RouterSnapshot>("/network/snapshot"),
        apiClient.get<{ anomalies: Record<string, unknown>[] }>("/network/anomalies"),
      ]);
      set((state) => {
        const updatedHistory = [...state.history, snapshotRes.data].slice(-20);
        return {
          snapshot: snapshotRes.data,
          anomalies: anomaliesRes.data.anomalies,
          loading: false,
          history: updatedHistory,
        };
      });
    } catch (error) {
      set({ error: "Failed to fetch metrics", loading: false });
    }
  },
  startAutoRefresh: () => {
    void get().fetchSnapshot();
    const interval = window.setInterval(() => {
      void get().fetchSnapshot();
    }, 15000);
    return () => window.clearInterval(interval);
  },
}));

