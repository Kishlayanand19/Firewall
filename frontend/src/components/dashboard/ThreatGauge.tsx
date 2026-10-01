"use client";

import { motion } from "framer-motion";
import { cn, formatThreatLevel, getThreatColor } from "@/lib/utils";

interface ThreatGaugeProps {
  score: number;
  threatLevel: string;
  label?: string;
}

export function ThreatGauge({ score, threatLevel, label = "Cognitive Threat" }: ThreatGaugeProps) {
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? "#ef4444" : score >= 50 ? "#f97316" : score >= 30 ? "#f59e0b" : "#22c55e";

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-40 h-40">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(56,189,248,0.1)" strokeWidth="8" />
          <motion.circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-bold"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {Math.round(score)}
          </motion.span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>
      <p className="mt-2 text-sm text-slate-400">{label}</p>
      <p className={cn("text-sm font-semibold capitalize", getThreatColor(threatLevel))}>
        {formatThreatLevel(threatLevel)}
      </p>
    </div>
  );
}
