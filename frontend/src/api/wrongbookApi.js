import { request } from "./http";
export function fetchWrongQuestions() { return request("/wrong-questions"); }
export function createWrongQuestion(payload) { return request("/wrong-questions", { method: "POST", body: JSON.stringify(payload) }); }
export function updateWrongQuestionStatus(id, status) { return request(`/wrong-questions/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }); }
export function deleteWrongQuestion(id) { return request(`/wrong-questions/${id}`, { method: "DELETE" }); }
