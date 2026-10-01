"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { AlertTriangle, Shield, HelpCircle, RefreshCw } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { ThreatGauge } from "@/components/dashboard/ThreatGauge";
import { cn, getThreatBg, formatThreatLevel } from "@/lib/utils";
import type { AnalysisResult } from "@/lib/types";

interface AnalysisResultsProps {
  result: AnalysisResult;
}

export function AnalysisResults({ result }: AnalysisResultsProps) {
  const [showExplain, setShowExplain] = useState(false);
  const scores = result.scores;

  const radarData = [
    { subject: "Manipulation", value: scores.manipulation_score },
    { subject: "Emotional", value: scores.emotional_pressure_score },
    { subject: "Misinfo", value: scores.misinformation_probability },
    { subject: "Propaganda", value: scores.propaganda_risk },
    { subject: "SocEng", value: scores.social_engineering_risk },
  ];

  const timeline = result.threat_report?.risk_timeline || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className={cn("p-4 rounded-xl border flex items-center gap-4", getThreatBg(scores.threat_level))}>
        <AlertTriangle className="h-8 w-8 shrink-0" />
        <div>
          <p className="font-semibold">Threat Level: {formatThreatLevel(scores.threat_level)}</p>
          <p className="text-sm opacity-80">{result.threat_report?.summary || result.threat_report?.explainability?.why_flagged}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="flex items-center justify-center">
          <ThreatGauge score={scores.cognitive_threat_level} threatLevel={scores.threat_level} />
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Threat Vector Radar</CardTitle>
          </CardHeader>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(56,189,248,0.2)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Radar name="Score" dataKey="value" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Manipulation", value: scores.manipulation_score },
          { label: "Emotional Pressure", value: scores.emotional_pressure_score },
          { label: "Misinformation", value: scores.misinformation_probability },
          { label: "Trust Index", value: scores.trustworthiness_index },
        ].map((s) => (
          <Card key={s.label} className="text-center py-4">
            <p className="text-2xl font-bold text-sky-300">{Math.round(s.value)}</p>
            <p className="text-xs text-slate-400 mt-1">{s.label}</p>
          </Card>
        ))}
      </div>

      <Card className="border-purple-500/30">
        <div className="flex items-center gap-2 mb-3">
          <RefreshCw className="h-5 w-5 text-purple-400" />
          <h3 className="font-semibold">AI Reframing — Safe Interpretation</h3>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">{result.reframed_interpretation}</p>
      </Card>

      {timeline.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Risk Timeline</CardTitle>
          </CardHeader>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(56,189,248,0.1)" />
              <XAxis dataKey="stage" tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #38bdf8" }} />
              <Line type="monotone" dataKey="cumulative_risk" stroke="#a855f7" strokeWidth={2} dot={{ fill: "#a855f7" }} />
              <Line type="monotone" dataKey="risk_value" stroke="#38bdf8" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      <Card>
        <button
          onClick={() => setShowExplain(!showExplain)}
          className="flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors w-full"
        >
          <HelpCircle className="h-5 w-5" />
          <span className="font-medium">Why was this flagged?</span>
        </button>
        {showExplain && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            className="mt-4 space-y-4 border-t border-sky-500/20 pt-4"
          >
            <ExplainSection title="Persuasive Phrases" items={result.threat_report?.persuasive_phrases} />
            <ExplainSection title="Emotional Triggers" items={result.threat_report?.emotional_triggers} />
            <ExplainSection title="Misinformation Signals" items={result.threat_report?.misinformation_signals} />
            <ExplainSection title="Persuasion Techniques" items={result.threat_report?.persuasion_techniques} />
          </motion.div>
        )}
      </Card>

      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Shield className="h-5 w-5 text-sky-400" />
          <CardTitle>Agent Findings</CardTitle>
        </div>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {result.agent_findings.map((agent) => (
            <div key={agent.agent_id} className="p-3 rounded-lg bg-black/30 border border-slate-700/50">
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium">{agent.agent_name}</span>
                <span className="text-xs text-sky-400">{(agent.confidence * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-slate-400">{agent.reasoning}</p>
            </div>
          ))}
        </div>
      </Card>
    </motion.div>
  );
}

function ExplainSection({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) return null;
  return (
    <div>
      <p className="text-sm font-medium text-purple-300 mb-2">{title}</p>
      <ul className="flex flex-wrap gap-2">
        {items.map((item, i) => (
          <span key={i} className="text-xs px-2 py-1 rounded bg-red-500/10 border border-red-500/30 text-red-300">
            {item}
          </span>
        ))}
      </ul>
    </div>
  );
}
