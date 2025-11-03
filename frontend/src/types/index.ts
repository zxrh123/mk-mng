export type InterfaceMetric = {
  name: string;
  rx_rate: number;
  tx_rate: number;
  rx_packets: number;
  tx_packets: number;
  status: string;
};

export type NetworkMetrics = {
  cpu_load: number;
  memory_usage: number;
  latency_ms: number;
  packet_loss: number;
  interfaces: InterfaceMetric[];
  updated_at: string;
};

export type RouterSnapshot = {
  router_identifier: string;
  metrics: NetworkMetrics;
};

export type AIPlanStep = {
  description: string;
  order: number;
  command_preview?: string | null;
};

export type AIExecutionPlan = {
  intent: string;
  confidence: number;
  steps: AIPlanStep[];
  requires_approval: boolean;
};

export type AIScript = {
  language?: string;
  contents: string;
  safe?: boolean;
};

export type AICommandResponse = {
  plan: AIExecutionPlan;
  script: AIScript | null;
  auto_execute: boolean;
  metadata: {
    decision_id: string;
    knowledge: string[];
    anomalies: Record<string, unknown>[];
  };
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  status?: "streaming" | "complete";
  decisionId?: string;
};

