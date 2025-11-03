import { useEffect, useMemo, useRef, useState } from "react";

export interface ChatMessage {
  sender: "user" | "assistant";
  content: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

interface SendPayload {
  message: string;
  host?: string;
}

export function useWebSocketChat(sessionId: string, host?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const origin = window.location.origin.replace("http", "ws");
    const socket = new WebSocket(`${origin}/ws/assistant?session_id=${sessionId}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          content: data.message,
          metadata: data.metadata,
          timestamp: new Date().toISOString()
        }
      ]);
      setIsThinking(false);
    };

    socket.onerror = () => setIsThinking(false);
    socket.onclose = () => setIsThinking(false);

    return () => {
      socket.close();
    };
  }, [sessionId]);

  const sendMessage = (payload: SendPayload) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        content: payload.message,
        timestamp: new Date().toISOString()
      }
    ]);
    setIsThinking(true);
    socketRef.current.send(
      JSON.stringify({
        message: payload.message,
        host: payload.host ?? host
      })
    );
  };

  return useMemo(
    () => ({
      messages,
      isThinking,
      sendMessage
    }),
    [messages, isThinking]
  );
}
