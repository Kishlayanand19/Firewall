"use client";

import { motion } from "framer-motion";
import { Bot, CheckCircle, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { AgentFinding } from "@/lib/types";

const AGENT_ORDER = [
  "content_analysis",
  "emotional_influence",
  "persuasion_manipulation",
  "misinformation",
  "social_engineering",
  "behavioral_reasoning",
  "safety_advisor",
];

const AGENT_LABELS: Record<string, string> = {
  content_analysis: "Content Analysis",
  emotional_influence: "Emotional Influence",
  persuasion_manipulation: "Persuasion & Manipulation",
  misinformation: "Misinformation Detection",
  social_engineering: "Social Engineering",
  behavioral_reasoning: "Behavioral Reasoning",
  safety_advisor: "Safety Advisor",
};

interface AgentPipelineProps {
  agents: AgentFinding[];
  pipelineStep: string;
}

export function AgentPipeline({ agents, pipelineStep }: AgentPipelineProps) {
  const completedIds = new Set(agents.map((a) => a.agent_id));
  const activeId = AGENT_ORDER.find((id) => !completedIds.has(id)) ?? null;

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
        <span className="text-sm text-sky-300 terminal-text">{pipelineStep}</span>
      </div>
      <div className="space-y-3">
        {AGENT_ORDER.map((id) => {
          const agent = agents.find((a) => a.agent_id === id);
          const isComplete = completedIds.has(id);
          const isActive = activeId === id;

          return (
            <motion.div
              key={id}
              layout
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex items-start gap-3 p-3 rounded-lg border ${
                isComplete
                  ? "border-green-500/30 bg-green-500/5"
                  : isActive
                  ? "border-sky-500/50 bg-sky-500/10"
                  : "border-slate-700/50 bg-black/20"
              }`}
            >
              {isComplete ? (
                <CheckCircle className="h-5 w-5 text-green-400 shrink-0 mt-0.5" />
              ) : isActive ? (
                <Loader2 className="h-5 w-5 text-sky-400 animate-spin shrink-0 mt-0.5" />
              ) : (
                <Bot className="h-5 w-5 text-slate-600 shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center gap-2">
                  <span className="text-sm font-medium">
                    {agent?.agent_name || AGENT_LABELS[id] || id}
                  </span>
                  {agent && (
                    <span className="text-xs text-sky-400 shrink-0">
                      {(agent.confidence * 100).toFixed(0)}%
                      {agent.duration_ms ? ` · ${agent.duration_ms}ms` : ""}
                    </span>
                  )}
                </div>
                {agent?.reasoning && (
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{agent.reasoning}</p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
}
