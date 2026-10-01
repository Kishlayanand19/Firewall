"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bot, Cpu, Network } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { getAgentRegistry } from "@/lib/api";

interface AgentInfo {
  id: string;
  name: string;
  role: string;
  status: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);

  useEffect(() => {
    getAgentRegistry().then((data) => setAgents(data.agents || []));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold gradient-text">AI Agent Monitor</h1>
        <p className="text-slate-400 mt-1">Multi-agent orchestration and communication visualization</p>
      </div>

      <Card className="mb-8 border-purple-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            Agent Communication Graph
          </CardTitle>
        </CardHeader>
        <div className="flex flex-wrap justify-center gap-2 py-6">
          {agents.map((agent, i) => (
            <div key={agent.id} className="flex items-center">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="px-4 py-2 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sm text-center min-w-[120px]"
              >
                <Bot className="h-4 w-4 mx-auto mb-1 text-sky-400" />
                {agent.name.split(" ")[0]}
              </motion.div>
              {i < agents.length - 1 && (
                <span className="text-sky-500/50 mx-1">→</span>
              )}
            </div>
          ))}
          <span className="text-sky-500/50 mx-1">→</span>
          <div className="px-4 py-2 rounded-lg bg-purple-500/10 border border-purple-500/30 text-sm text-center">
            <Cpu className="h-4 w-4 mx-auto mb-1 text-purple-400" />
            Synthesis
          </div>
        </div>
      </Card>

      <div className="grid md:grid-cols-2 gap-4">
        {agents.map((agent, i) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <Card>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-sky-400" />
                  <h3 className="font-semibold">{agent.name}</h3>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                  {agent.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-3">{agent.role}</p>
              <div className="mt-3 flex items-center gap-2">
                <div className="flex-1 h-1.5 rounded-full bg-slate-800">
                  <div className="h-full w-3/4 rounded-full bg-gradient-to-r from-sky-500 to-purple-500" />
                </div>
                <span className="text-xs text-sky-400">75% avg conf</span>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
