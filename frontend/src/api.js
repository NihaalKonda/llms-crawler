const API_BASE = process.env.API_BASE || "http://localhost:8000";

export async function crawlSite(url) {
  const res = await fetch(`${API_BASE}/api/crawl`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    try {
      const errorData = await res.json();
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    } catch (e) {
      if (e.message) throw e;
      throw new Error(`Request failed with status ${res.status}`);
    }
  }

  const data = await res.json();
  return data;
}