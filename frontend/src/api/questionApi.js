import { request } from "./http";

export function generateQuestions({ topic, questionType, difficulty, count, model, documentId }) {
  return request("/questions/generate", {
    method: "POST",
    body: JSON.stringify({
      topic,
      question_type: questionType,
      difficulty,
      count: Number(count),
      model,
      document_id: documentId || null,
    }),
  });
}

export function generateSummary({ topic, useRag, model, documentId }) {
  return request("/summary", {
    method: "POST",
    body: JSON.stringify({
      topic,
      use_rag: useRag,
      model,
      document_id: documentId || null,
    }),
  });
}

export function fetchGenerationHistory({ recordType = "", limit = 50 } = {}) {
  const params = new URLSearchParams();
  if (recordType) params.set("record_type", recordType);
  params.set("limit", String(limit));
  return request(`/generations?${params.toString()}`);
}

export function deleteGenerationRecord(id) {
  return request(`/generations/${id}`, { method: "DELETE" });
}
