"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";
import { Activity, Shield, AlertTriangle, TrendingUp } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { ThreatGauge } from "@/components/dashboard/ThreatGauge";
import { getDashboardStats } from "@/lib/api";
import type { DashboardStats } from "@/lib/types";
import { formatThreatLevel, getThreatBg } from "@/lib/utils";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => setStats(null));
  }, []);

  const heatmapData = stats
    ? Object.entries(stats.emotional_heatmap).map(([emotion, value]) => ({ emotion, value }))
    : [];

  const threatDist = stats
    ? Object.entries(stats.threat_distribution).map(([level, count]) => ({
        level: formatThreatLevel(level),
        count,
      }))
    : [];

  const avgThreat = stats?.avg_manipulation_score || 35;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold gradient-text">Threat Dashboard</h1>
        <p className="text-slate-400 mt-1">Real-time cognitive security overview</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { icon: Activity, label: "Total Analyses", value: stats?.total_analyses ?? 0, color: "text-sky-400" },
          { icon: AlertTriangle, label: "Threats Detected", value: stats?.threats_detected ?? 0, color: "text-red-400" },
          { icon: TrendingUp, label: "Avg Manipulation", value: `${stats?.avg_manipulation_score?.toFixed(0) ?? 0}%`, color: "text-orange-400" },
          { icon: Shield, label: "Agents Active", value: 7, color: "text-green-400" },
        ].map((item) => (
          <Card key={item.label} className="flex items-center gap-4">
            <item.icon className={`h-8 w-8 ${item.color}`} />
            <div>
              <p className="text-2xl font-bold">{item.value}</p>
              <p className="text-xs text-slate-400">{item.label}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <Card className="flex items-center justify-center py-6">
          <ThreatGauge
            score={avgThreat}
            threatLevel={avgThreat > 60 ? "dangerous" : avgThreat > 40 ? "manipulative" : "mild_influence"}
            label="Avg Cognitive Threat"
          />
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Manipulation Trend (7 days)</CardTitle>
          </CardHeader>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={stats?.manipulation_trend || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(56,189,248,0.1)" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #38bdf8" }} />
              <Line type="monotone" dataKey="score" stroke="#38bdf8" strokeWidth={2} dot={{ fill: "#38bdf8" }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Emotional Attack Heatmap</CardTitle>
          </CardHeader>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={heatmapData}>
              <PolarGrid stroke="rgba(168,85,247,0.2)" />
              <PolarAngleAxis dataKey="emotion" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Radar dataKey="value" stroke="#a855f7" fill="#a855f7" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Threat Distribution</CardTitle>
          </CardHeader>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={threatDist}>
              <XAxis dataKey="level" tick={{ fill: "#64748b", fontSize: 9 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #38bdf8" }} />
              <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Threats</CardTitle>
        </CardHeader>
        {stats?.recent_threats?.length ? (
          <div className="space-y-3">
            {stats.recent_threats.map((t) => (
              <div
                key={t.id}
                className={`p-3 rounded-lg border flex justify-between items-start gap-4 ${getThreatBg(t.threat_level)}`}
              >
                <p className="text-sm flex-1 line-clamp-2">{t.content_preview}</p>
                <div className="text-right shrink-0">
                  <p className="text-xs font-medium">{formatThreatLevel(t.threat_level)}</p>
                  <p className="text-xs text-slate-500">{Math.round(t.manipulation_score)}% manip</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500 text-center py-8">
            No analyses yet. Run the Live Analyzer to populate your dashboard.
          </p>
        )}
      </Card>
    </div>
  );
}
