import { nanoid } from "nanoid";
import { create } from "zustand";
import { apiClient } from "@/lib/api";
import type { AICommandResponse, ChatMessage } from "@/types";

type AIState = {
  messages: ChatMessage[];
  lastResponse: AICommandResponse | null;
  sending: boolean;
  error: string | null;
  sendCommand: (content: string) => Promise<void>;
  approveDecision: (decisionId: string) => Promise<void>;
  appendMessage: (message: ChatMessage) => void;
  setLastResponse: (response: AICommandResponse) => void;
  reset: () => void;
};

export const useAIStore = create<AIState>((set, get) => ({
  messages: [],
  lastResponse: null,
  sending: false,
  error: null,
  appendMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  setLastResponse: (response) => set({ lastResponse: response }),
  sendCommand: async (content) => {
    const userMessage: ChatMessage = {
      id: nanoid(),
      role: "user",
      content,
      createdAt: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, userMessage],
      sending: true,
      error: null,
    }));

    try {
      const response = await apiClient.post<AICommandResponse>("/ai/command", {
        message: content,
        actor: "operator",
      });

      set((state) => ({
        messages: [
          ...state.messages,
          {
            id: nanoid(),
            role: "assistant",
            content: `Intent: ${response.data.plan.intent}\nConfidence: ${(response.data.plan.confidence * 100).toFixed(1)}%`,
            createdAt: new Date().toISOString(),
            status: "complete",
            decisionId: response.data.metadata.decision_id,
          },
        ],
        lastResponse: response.data,
        sending: false,
      }));
    } catch (error) {
      set({ error: "Failed to reach AI core", sending: false });
    }
  },
  approveDecision: async (decisionId) => {
    try {
      await apiClient.post("/ai/decision/execute", {
        decision_id: decisionId,
        metadata: { approvedBy: "operator" },
      });
    } catch (error) {
      set({ error: "Execution failed" });
    }
  },
  reset: () => set({ messages: [], lastResponse: null, error: null }),
}));

