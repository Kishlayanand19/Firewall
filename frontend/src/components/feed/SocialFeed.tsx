"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, MessageCircle, Share2, Heart } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { streamAnalysis } from "@/lib/api";
import { cn, getThreatBg, formatThreatLevel } from "@/lib/utils";
import type { AnalysisResult } from "@/lib/types";

const FEED_POSTS = [
  {
    id: "1",
    author: "@news_alert_daily",
    avatar: "N",
    content: "BREAKING: Scientists HATE this one trick! Big Pharma is hiding the cure. Share before they delete this!!!",
    time: "2m ago",
    likes: 12400,
  },
  {
    id: "2",
    author: "@tech_updates",
    avatar: "T",
    content: "Apple announced new M4 chips with 40% better performance. Read the full analysis on our blog.",
    time: "15m ago",
    likes: 892,
  },
  {
    id: "3",
    author: "@urgent_notice",
    avatar: "U",
    content: "URGENT: Your Microsoft account has unusual activity. Verify immediately: http://micros0ft-verify.com/login",
    time: "1h ago",
    likes: 23,
  },
  {
    id: "4",
    author: "@wellness_guru",
    avatar: "W",
    content: "Only 3 spots left!!! Join my exclusive program NOW or you'll regret it forever. DM me ASAP!!!",
    time: "3h ago",
    likes: 456,
  },
];

export function SocialFeed() {
  const [analyses, setAnalyses] = useState<Record<string, AnalysisResult>>({});
  const [scanning, setScanning] = useState<string | null>(null);

  const analyzePost = (postId: string, content: string) => {
    setScanning(postId);
    streamAnalysis(
      content,
      (event) => {
        if (event.event === "analysis_complete") {
          setAnalyses((prev) => ({
            ...prev,
            [postId]: {
              id: String(event.id),
              content,
              content_type: "social",
              scores: event.scores as AnalysisResult["scores"],
              agent_findings: [],
              threat_report: (event.threat_report as AnalysisResult["threat_report"]) || {},
              reframed_interpretation: String(event.reframed_interpretation || ""),
              full_report: {},
            },
          }));
          setScanning(null);
        }
      },
      () => setScanning(null),
      () => setScanning(null)
    );
  };

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <p className="text-sm text-slate-400 mb-6 text-center">
        Simulated social feed — analyze posts to detect cognitive threats
      </p>
      {FEED_POSTS.map((post, i) => {
        const analysis = analyses[post.id];
        const threatLevel = analysis?.scores?.threat_level;
        const isDangerous = threatLevel && threatLevel !== "safe" && threatLevel !== "mild_influence";

        return (
          <motion.div
            key={post.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card
              className={cn(
                "relative overflow-hidden transition-all",
                isDangerous && "ring-2 ring-red-500/50 glow-border",
                analysis && threatLevel && getThreatBg(threatLevel)
              )}
            >
              {isDangerous && (
                <div className="absolute top-2 right-2 flex items-center gap-1 text-red-400 text-xs">
                  <AlertTriangle className="h-4 w-4" />
                  FLAGGED
                </div>
              )}
              <div className="flex gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sky-500 to-purple-600 flex items-center justify-center font-bold text-sm">
                  {post.avatar}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{post.author}</span>
                    <span className="text-xs text-slate-500">{post.time}</span>
                  </div>
                  <p className="mt-2 text-sm leading-relaxed">{post.content}</p>
                  <div className="flex items-center gap-6 mt-3 text-slate-500">
                    <button className="flex items-center gap-1 text-xs hover:text-red-400">
                      <Heart className="h-4 w-4" /> {post.likes}
                    </button>
                    <button className="flex items-center gap-1 text-xs hover:text-sky-400">
                      <MessageCircle className="h-4 w-4" />
                    </button>
                    <button className="flex items-center gap-1 text-xs hover:text-sky-400">
                      <Share2 className="h-4 w-4" />
                    </button>
                  </div>
                  {analysis && (
                    <div className="mt-3 p-3 rounded-lg bg-black/40 border border-sky-500/20 text-xs">
                      <p className="text-sky-300 font-medium">
                        Threat: {formatThreatLevel(analysis.scores.threat_level)} ({Math.round(analysis.scores.cognitive_threat_level)}/100)
                      </p>
                      <p className="text-slate-400 mt-1">{analysis.reframed_interpretation}</p>
                    </div>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-3"
                    disabled={scanning === post.id}
                    onClick={() => analyzePost(post.id, post.content)}
                  >
                    {scanning === post.id ? "Scanning..." : "Analyze Post"}
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}
