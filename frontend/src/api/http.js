/**
 * 前端 HTTP 请求封装。
 *
 * 端口说明：
 * - 后端地址不在这里手写；
 * - Vite 会读取项目根目录 project.config.json；
 * - vite.config.js 会把最终 API 地址注入为 __APP_CONFIG__.apiBaseUrl。
 *
 * 修改后端端口时，只需要改 project.config.json 中的 backend.port，
 * 然后重启前端 dev 服务即可。
 */
const API_BASE_URL = __APP_CONFIG__.apiBaseUrl;

function buildRequestOptions(options = {}) {
  const headers = { ...(options.headers || {}) };

  // 只有在请求体是 JSON 字符串时才添加 Content-Type。
  // GET 请求没有请求体，不需要 Content-Type；否则浏览器会先发 OPTIONS 预检请求。
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  return {
    ...options,
    headers,
  };
}

async function parseErrorMessage(response, fallbackMessage) {
  try {
    const data = await response.json();
    return data.detail || data.message || fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

export async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, buildRequestOptions(options));

  if (!response.ok) {
    const message = await parseErrorMessage(response, `请求失败：HTTP ${response.status}`);
    throw new Error(message);
  }

  return response.json();
}

export async function uploadRequest(path, formData) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await parseErrorMessage(response, `上传失败：HTTP ${response.status}`);
    throw new Error(message);
  }

  return response.json();
}
