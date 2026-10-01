"use client";

import { useEffect, useState } from "react";
import { Globe, Shield, AlertCircle } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { getSourceIntelligence } from "@/lib/api";

interface Source {
  domain: string;
  reputation_score: number;
  category: string;
  flags: string[];
}

export default function ThreatIntelPage() {
  const [sources, setSources] = useState<Source[]>([]);

  useEffect(() => {
    getSourceIntelligence().then((data) => setSources(data.sources || []));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold gradient-text">Threat Intelligence</h1>
        <p className="text-slate-400 mt-1">Source reputation engine and cognitive attack mapping</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {[
          { label: "Sources Tracked", value: sources.length || 3, icon: Globe },
          { label: "Low Reputation", value: sources.filter((s) => s.reputation_score < 40).length, icon: AlertCircle },
          { label: "Verified Safe", value: sources.filter((s) => s.reputation_score >= 70).length, icon: Shield },
        ].map((item) => (
          <Card key={item.label} className="flex items-center gap-4">
            <item.icon className="h-8 w-8 text-sky-400" />
            <div>
              <p className="text-2xl font-bold">{item.value}</p>
              <p className="text-xs text-slate-400">{item.label}</p>
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Source Credibility Tracker</CardTitle>
        </CardHeader>
        <div className="space-y-3">
          {sources.map((source) => (
            <div
              key={source.domain}
              className="flex items-center justify-between p-4 rounded-lg bg-black/30 border border-slate-700/50"
            >
              <div>
                <p className="font-medium text-sm">{source.domain}</p>
                <p className="text-xs text-slate-500 capitalize">{source.category}</p>
                {source.flags.length > 0 && (
                  <div className="flex gap-1 mt-1">
                    {source.flags.map((f) => (
                      <span key={f} className="text-xs px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="text-right">
                <p className={`text-2xl font-bold ${
                  source.reputation_score >= 70 ? "text-green-400" :
                  source.reputation_score >= 40 ? "text-yellow-400" : "text-red-400"
                }`}>
                  {source.reputation_score}
                </p>
                <p className="text-xs text-slate-500">reputation</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
