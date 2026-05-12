import { request } from "./http";

export function sendChatMessage({ message, useRag, model }) {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ message, use_rag: useRag, model }),
  });
}

export function fetchChatHistory(limit = 30) {
  return request(`/chat/history?limit=${limit}`);
}

export function deleteChatHistoryItem(id) {
  return request(`/chat/history/${id}`, { method: "DELETE" });
}

export function clearChatHistory() {
  return request("/chat/history", { method: "DELETE" });
}
