export interface ThreatScores {
  manipulation_score: number;
  emotional_pressure_score: number;
  misinformation_probability: number;
  propaganda_risk: number;
  social_engineering_risk: number;
  trustworthiness_index: number;
  cognitive_threat_level: number;
  threat_level: string;
}

export interface AgentFinding {
  agent_id: string;
  agent_name: string;
  confidence: number;
  reasoning: string;
  findings: Record<string, unknown>;
  status: string;
  duration_ms?: number;
}

export interface ThreatReport {
  summary?: string;
  persuasive_phrases?: string[];
  emotional_triggers?: string[];
  misinformation_signals?: string[];
  persuasion_techniques?: string[];
  explainability?: {
    why_flagged?: string;
    key_signals?: string[];
    confidence?: number;
  };
  risk_timeline?: Array<{
    stage: string;
    risk_value: number;
    cumulative_risk: number;
    order: number;
  }>;
  agent_graph?: {
    nodes: Array<{ id: string; name: string; confidence: number }>;
    edges: Array<{ from: string; to: string; type: string }>;
  };
}

export interface AnalysisResult {
  id: string;
  content: string;
  content_type: string;
  scores: ThreatScores;
  agent_findings: AgentFinding[];
  threat_report: ThreatReport;
  reframed_interpretation: string;
  full_report: Record<string, unknown>;
  created_at?: string;
}

export interface StreamEvent {
  event: string;
  agent_id?: string;
  agent_name?: string;
  message?: string;
  confidence?: number;
  reasoning?: string;
  findings?: Record<string, unknown>;
  scores?: ThreatScores;
  agent_findings?: AgentFinding[];
  threat_report?: ThreatReport;
  reframed_interpretation?: string;
}

export interface DashboardStats {
  total_analyses: number;
  threats_detected: number;
  avg_manipulation_score: number;
  threat_distribution: Record<string, number>;
  recent_threats: Array<{
    id: string;
    content_preview: string;
    threat_level: string;
    manipulation_score: number;
    cognitive_threat_level: number;
    created_at: string;
  }>;
  agent_activity: Array<{ agent: string; runs: number; avg_confidence: number }>;
  manipulation_trend: Array<{ date: string; score: number }>;
  emotional_heatmap: Record<string, number>;
}
