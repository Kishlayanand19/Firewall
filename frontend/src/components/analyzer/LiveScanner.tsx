"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Scan, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { streamAnalysis } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import type { AnalysisResult, AgentFinding } from "@/lib/types";
import { AgentPipeline } from "./AgentPipeline";
import { AnalysisResults } from "./AnalysisResults";

const SAMPLE_TEXTS = [
  "BREAKING: They don't want you to know this secret cure! Share before deleted!!!",
  "URGENT: Your account will be suspended. Click here to verify your password immediately.",
  "You MUST buy this now or you'll regret it forever. Only 3 left!!!",
];

const PHASE_LABELS: Record<string, string> = {
  independent: "Analyzing content and emotional signals…",
  dependent: "Checking persuasion, misinformation, and social engineering…",
  synthesis: "Building final threat assessment…",
};

export function LiveScanner() {
  const [content, setContent] = useState("");
  const [pipelineStep, setPipelineStep] = useState("");
  const { isAnalyzing, setIsAnalyzing, streamingAgents, setStreamingAgents, setCurrentAnalysis, addNotification } = useAppStore();
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = useCallback(() => {
    if (!content.trim() || isAnalyzing) return;
    setIsAnalyzing(true);
    setResult(null);
    setStreamingAgents([]);
    setPipelineStep("Starting analysis pipeline…");

    const cancel = streamAnalysis(
      content,
      (event) => {
        const ev = event.event as string;
        if (ev === "pipeline_start") {
          setPipelineStep("Pipeline started");
        } else if (ev === "phase_start") {
          const phase = String(event.phase || "");
          setPipelineStep(PHASE_LABELS[phase] || String(event.message || "Running agents…"));
        } else if (ev === "phase_complete") {
          setPipelineStep(`Phase complete (${event.elapsed_ms}ms)`);
        } else if (ev === "synthesis_start") {
          setPipelineStep("Synthesizing final assessment…");
        } else if (ev === "agent_start") {
          setPipelineStep(`${event.agent_name} running…`);
        } else if (ev === "agent_complete") {
          const finding: AgentFinding = {
            agent_id: String(event.agent_id),
            agent_name: String(event.agent_name),
            confidence: Number(event.confidence) || 0,
            reasoning: String(event.reasoning || ""),
            findings: (event.findings as Record<string, unknown>) || {},
            status: "completed",
            duration_ms: Number(event.duration_ms) || 0,
          };
          useAppStore.getState().addStreamingAgent(finding);
        } else if (ev === "analysis_complete") {
          const analysis: AnalysisResult = {
            id: String(event.id || crypto.randomUUID()),
            content,
            content_type: "text",
            scores: event.scores as AnalysisResult["scores"],
            agent_findings: (event.agent_findings as AgentFinding[]) || [],
            threat_report: (event.threat_report as AnalysisResult["threat_report"]) || {},
            reframed_interpretation: String(event.reframed_interpretation || ""),
            full_report: (event.full_report as Record<string, unknown>) || {},
          };
          setResult(analysis);
          setCurrentAnalysis(analysis);
          setPipelineStep("Analysis complete");
          const level = analysis.scores?.threat_level || "safe";
          if (level !== "safe") {
            addNotification(`Threat detected: ${level.replace(/_/g, " ")}`, "warning");
          }
        } else if (ev === "error") {
          addNotification(String(event.message || "Analysis failed"), "danger");
        }
      },
      (err) => {
        addNotification(err.message, "danger");
        setIsAnalyzing(false);
      },
      () => setIsAnalyzing(false)
    );

    return () => cancel();
  }, [content, isAnalyzing, setIsAnalyzing, setStreamingAgents, setCurrentAnalysis, addNotification]);

  return (
    <div className="space-y-6">
      <Card className="glow-border">
        <div className="flex items-center gap-2 mb-4">
          <Scan className="h-5 w-5 text-sky-400" />
          <h2 className="text-xl font-semibold">Live Content Scanner</h2>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste social media posts, emails, ads, headlines, or messages..."
          className="w-full h-40 rounded-lg bg-black/30 border border-sky-500/30 p-4 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-sky-500/50"
          disabled={isAnalyzing}
        />
        <div className="flex flex-wrap gap-2 mt-3">
          {SAMPLE_TEXTS.map((sample, i) => (
            <button
              key={i}
              onClick={() => setContent(sample)}
              className="text-xs px-3 py-1 rounded-full border border-purple-500/30 text-purple-300 hover:bg-purple-500/10 transition-colors"
            >
              Sample {i + 1}
            </button>
          ))}
        </div>
        <div className="flex justify-between items-center mt-4">
          <span className="text-xs text-slate-500">{content.length} / 50000 chars</span>
          <Button onClick={handleAnalyze} disabled={isAnalyzing || !content.trim()}>
            {isAnalyzing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Run AI Analysis
              </>
            )}
          </Button>
        </div>
      </Card>

      <AnimatePresence>
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <AgentPipeline agents={streamingAgents} pipelineStep={pipelineStep} />
          </motion.div>
        )}
      </AnimatePresence>

      {result && <AnalysisResults result={result} />}
    </div>
  );
}
