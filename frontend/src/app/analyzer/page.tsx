import { LiveScanner } from "@/components/analyzer/LiveScanner";

export default function AnalyzerPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold gradient-text">Live Content Analyzer</h1>
        <p className="text-slate-400 mt-1">
          Real-time multi-agent cognitive threat analysis with streaming pipeline
        </p>
      </div>
      <LiveScanner />
    </div>
  );
}
