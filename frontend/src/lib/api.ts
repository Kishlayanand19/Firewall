import type { AnalysisResult, DashboardStats } from "./types";
import { getApiBaseUrl, getApiOrigin } from "./env";

const API_BASE = getApiBaseUrl();

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body?.detail) {
      return typeof body.detail === "string" ? body.detail : "Request failed";
    }
  } catch {
    /* ignore */
  }
  return "Request failed";
}

export async function analyzeContent(content: string, contentType = "text"): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, content_type: contentType }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getReport(id: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/reports/${id}`);
  if (!res.ok) throw new Error("Report not found");
  return res.json();
}

export async function getHistory(limit = 20) {
  const res = await fetch(`${API_BASE}/reports/history/list?limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/reports/dashboard/stats`);
  if (!res.ok) {
    return {
      total_analyses: 0,
      threats_detected: 0,
      avg_manipulation_score: 0,
      threat_distribution: {},
      recent_threats: [],
      agent_activity: [],
      manipulation_trend: [],
      emotional_heatmap: {},
    };
  }
  return res.json();
}

export async function getAgentRegistry() {
  const res = await fetch(`${API_BASE}/agents/registry`);
  if (!res.ok) return { agents: [], total: 0 };
  return res.json();
}

export async function getSourceIntelligence() {
  const res = await fetch(`${API_BASE}/agents/intelligence/sources`);
  if (!res.ok) return { sources: [] };
  return res.json();
}

export function streamAnalysis(
  content: string,
  onEvent: (event: Record<string, unknown>) => void,
  onError?: (err: Error) => void,
  onComplete?: () => void
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/analyze/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, content_type: "text" }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) throw new Error(await parseError(res));

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(data);
            } catch {
              /* skip malformed */
            }
          }
        }
      }
      onComplete?.();
    } catch (e) {
      if ((e as Error).name !== "AbortError") onError?.(e as Error);
    }
  })();

  return () => controller.abort();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${getApiOrigin()}/api/v1/health`);
    return res.ok;
  } catch {
    return false;
  }
}
