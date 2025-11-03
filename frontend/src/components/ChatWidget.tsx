import { FormEvent, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageCircle, Send, X } from "lucide-react";

import { useWebSocketChat } from "../hooks/useWebSocketChat";
import { strings } from "../lib/strings";
import { Button } from "./ui/Button";

const generateSessionId = () => crypto.randomUUID();

export const ChatWidget = ({ host }: { host?: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sessionId] = useState(generateSessionId);
  const { messages, isThinking, sendMessage } = useWebSocketChat(sessionId, host);

  const lastFiveMessages = useMemo(() => messages.slice(-50), [messages]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;
    sendMessage({ message: input.trim(), host });
    setInput("");
  };

  return (
    <div className="fixed bottom-10 left-10 z-50 flex flex-col items-end gap-4">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3 }}
            className="w-96 overflow-hidden rounded-3xl border border-neon/40 bg-midnight/95 shadow-neon"
          >
            <div className="flex items-center justify-between bg-glass px-5 py-4">
              <div>
                <h3 className="text-lg font-bold text-neon">{strings.chat.title}</h3>
                <p className="text-xs text-azure/70">{strings.chat.subtitle}</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-full bg-magenta/20 p-2 text-magenta transition hover:bg-magenta/40"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex max-h-80 flex-col gap-3 overflow-y-auto px-5 py-4">
              {lastFiveMessages.map((message, index) => (
                <div
                  key={`${message.timestamp}-${index}`}
                  className={`
                    rounded-2xl px-4 py-3 text-sm shadow-lg
                    ${message.sender === "assistant" ? "self-start bg-azure/15 text-white" : "self-end bg-neon text-midnight"}
                  `}
                >
                  <p>{message.content}</p>
                </div>
              ))}
              {isThinking && (
                <div className="self-start rounded-2xl bg-azure/10 px-4 py-2 text-xs text-azure/80">
                  {strings.chat.processing}
                </div>
              )}
            </div>
            <form onSubmit={handleSubmit} className="border-t border-azure/20 bg-midnight/80 px-5 py-4">
              <div className="flex items-center gap-3">
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  className="flex-1 rounded-full border border-azure/30 bg-transparent px-4 py-2 text-sm text-white placeholder:text-azure/40 focus:border-neon focus:outline-none"
                  placeholder={strings.chat.placeholder}
                />
                <Button type="submit" variant="secondary" className="px-3">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <Button
        variant="primary"
        className="h-14 w-14 rounded-full shadow-glow"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    </div>
  );
};
