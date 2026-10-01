import { create } from "zustand";
import type { AnalysisResult, AgentFinding } from "./types";

interface AppState {
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;
  toggleTheme: () => void;
  currentAnalysis: AnalysisResult | null;
  setCurrentAnalysis: (a: AnalysisResult | null) => void;
  streamingAgents: AgentFinding[];
  setStreamingAgents: (agents: AgentFinding[]) => void;
  addStreamingAgent: (agent: AgentFinding) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (v: boolean) => void;
  notifications: Array<{ id: string; message: string; type: "info" | "warning" | "danger" }>;
  addNotification: (message: string, type?: "info" | "warning" | "danger") => void;
  clearNotifications: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: "dark",
  setTheme: (theme) => set({ theme }),
  toggleTheme: () =>
    set((s) => {
      const next = s.theme === "dark" ? "light" : "dark";
      if (typeof document !== "undefined") {
        document.documentElement.setAttribute("data-theme", next);
      }
      return { theme: next };
    }),
  currentAnalysis: null,
  setCurrentAnalysis: (currentAnalysis) => set({ currentAnalysis }),
  streamingAgents: [],
  setStreamingAgents: (streamingAgents) => set({ streamingAgents }),
  addStreamingAgent: (agent) =>
    set((s) => ({
      streamingAgents: [
        ...s.streamingAgents.filter((a) => a.agent_id !== agent.agent_id),
        agent,
      ],
    })),
  isAnalyzing: false,
  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  notifications: [],
  addNotification: (message, type = "info") =>
    set((s) => ({
      notifications: [
        ...s.notifications,
        { id: crypto.randomUUID(), message, type },
      ].slice(-5),
    })),
  clearNotifications: () => set({ notifications: [] }),
}));
