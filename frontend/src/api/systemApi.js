import { request } from "./http";
export function fetchDashboard() { return request("/dashboard"); }
export function fetchModelStatus() { return request("/model/status"); }

export function fetchModelList() { return request("/models"); }
