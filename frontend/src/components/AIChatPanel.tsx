import { FormEvent, useEffect, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { motion } from "framer-motion";
import { Bot, Loader2, Send, User } from "lucide-react";
import { nanoid } from "nanoid";

import { websocketUrl } from "@/lib/api";
import { useAIStore } from "@/store/useAIStore";
import type { AICommandResponse } from "@/types";

export const AIChatPanel = () => {
  const [input, setInput] = useState("");
  const { messages, sendCommand, sending, error, appendMessage, setLastResponse } = useAIStore();

  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket<AICommandResponse>(websocketUrl, {
    shouldReconnect: () => true,
  });

  useEffect(() => {
    if (!lastJsonMessage) return;
    const payload = lastJsonMessage;

    if (payload?.plan) {
      setLastResponse(payload);
      const exists = messages.some(
        (msg) => msg.decisionId && payload.metadata?.decision_id && msg.decisionId === payload.metadata.decision_id,
      );
      if (!exists) {
        appendMessage({
          id: nanoid(),
          role: "assistant",
          content: `Intent: ${payload.plan.intent}\nConfidence: ${(payload.plan.confidence * 100).toFixed(1)}%`,
          createdAt: new Date().toISOString(),
          status: "complete",
          decisionId: payload.metadata?.decision_id,
        });
      }
    }
  }, [appendMessage, lastJsonMessage, messages, setLastResponse]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;
    const content = input.trim();
    setInput("");

    await sendCommand(content);

    if (readyState === ReadyState.OPEN) {
      sendJsonMessage({ message: content, actor: "operator" });
    }
  };

  return (
    <div className="flex h-full flex-col rounded-3xl border border-white/10 bg-white/5">
      <header className="flex items-center gap-3 border-b border-white/10 px-6 py-4">
        <span className="rounded-full bg-brand/15 p-2">
          <Bot className="h-5 w-5 text-brand" />
        </span>
        <div>
          <h2 className="font-heading text-lg text-white">??????? ?????</h2>
          <p className="text-xs text-white/50">
            ??????: {readyState === ReadyState.OPEN ? "????" : "????? ???????"}
          </p>
        </div>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-4">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm leading-relaxed text-white ${
                message.role === "user" ? "bg-brand/20 border-brand/40" : ""
              }`}
            >
              <div className="flex items-center gap-2 text-xs text-white/50">
                {message.role === "user" ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
                <span>{new Date(message.createdAt).toLocaleTimeString()}</span>
              </div>
              <p className="mt-2 whitespace-pre-wrap">{message.content}</p>
            </div>
          </motion.div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-xs text-white/60">
              <Loader2 className="h-4 w-4 animate-spin text-brand" />
              ???? ????? ?????...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-white/10 p-4">
        <div className="flex items-center gap-3 rounded-2xl bg-black/30 px-4 py-2">
          <input
            className="flex-1 bg-transparent text-sm text-white placeholder:text-white/40 focus:outline-none"
            placeholder="?? ??????? ?? ???? ???? ?????..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-full bg-brand px-4 py-2 text-xs font-semibold text-white transition hover:bg-brand-magenta disabled:cursor-not-allowed disabled:opacity-50"
            disabled={sending}
          >
            <Send className="h-4 w-4" />
            ?????
          </button>
        </div>
        {error && <p className="mt-2 text-xs text-red-400">{error}</p>}
      </form>
    </div>
  );
};


