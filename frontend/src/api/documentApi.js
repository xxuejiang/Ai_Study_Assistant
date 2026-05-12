import { request, uploadRequest } from "./http";
export function fetchDocuments() { return request("/documents"); }
export function uploadDocument(file) { const fd = new FormData(); fd.append("file", file); return uploadRequest("/documents/upload", fd); }
export function fetchDocumentChunks(id) { return request(`/documents/${id}/chunks`); }
export function deleteDocument(id) { return request(`/documents/${id}`, { method: "DELETE" }); }
