import { Card, CardHeader, CardTitle } from "@/components/ui/card";

const endpoints = [
  { method: "POST", path: "/api/v1/analyze", desc: "Analyze content (full JSON response)" },
  { method: "POST", path: "/api/v1/analyze/stream", desc: "Stream analysis via SSE (real-time agent events)" },
  { method: "GET", path: "/api/v1/reports/{id}", desc: "Fetch analysis report by ID" },
  { method: "GET", path: "/api/v1/reports/history/list", desc: "List analysis history" },
  { method: "GET", path: "/api/v1/reports/dashboard/stats", desc: "Dashboard statistics" },
  { method: "GET", path: "/api/v1/agents/registry", desc: "AI agent registry" },
  { method: "GET", path: "/api/v1/agents/intelligence/sources", desc: "Source reputation data" },
  { method: "GET", path: "/api/v1/health", desc: "Health check" },
];

export default function ApiDocsPage() {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://localhost:8000";

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold gradient-text mb-2">API Documentation</h1>
      <p className="text-slate-400 mb-8">Thought Firewall REST API v1.0</p>

      <Card className="mb-8 terminal-text text-sm">
        <p className="text-sky-400">Base URL: {base}</p>
        <p className="text-slate-500 mt-2">OpenAPI docs: {base}/docs</p>
      </Card>

      <div className="space-y-4">
        {endpoints.map((ep) => (
          <Card key={ep.path + ep.method}>
            <div className="flex items-start gap-4">
              <span className={`text-xs font-bold px-2 py-1 rounded shrink-0 ${
                ep.method === "POST" ? "bg-green-500/20 text-green-400" : "bg-sky-500/20 text-sky-400"
              }`}>
                {ep.method}
              </span>
              <div>
                <code className="text-sm text-purple-300">{ep.path}</code>
                <p className="text-sm text-slate-400 mt-1">{ep.desc}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Example: Stream Analysis</CardTitle>
        </CardHeader>
        <pre className="text-xs overflow-x-auto p-4 rounded-lg bg-black/40 border border-sky-500/20 text-slate-300">
{`curl -X POST ${base}/api/v1/analyze/stream \\
  -H "Content-Type: application/json" \\
  -d '{"content": "URGENT: Verify your account now!!!"}'`}
        </pre>
      </Card>
    </div>
  );
}
