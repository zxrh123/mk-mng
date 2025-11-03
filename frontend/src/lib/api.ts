import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
  timeout: 15000,
});

export const websocketUrl = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/api/ai/ws";

