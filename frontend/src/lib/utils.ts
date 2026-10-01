import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatThreatLevel(level: string): string {
  return level.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function getThreatColor(level: string): string {
  const map: Record<string, string> = {
    safe: "threat-safe",
    mild_influence: "threat-mild",
    manipulative: "threat-manipulative",
    dangerous: "threat-dangerous",
    coordinated_attack: "threat-coordinated",
  };
  return map[level] || "text-foreground";
}

export function getThreatBg(level: string): string {
  const map: Record<string, string> = {
    safe: "bg-green-500/20 border-green-500/40",
    mild_influence: "bg-yellow-500/20 border-yellow-500/40",
    manipulative: "bg-orange-500/20 border-orange-500/40",
    dangerous: "bg-red-500/20 border-red-500/40",
    coordinated_attack: "bg-red-600/30 border-red-600/50",
  };
  return map[level] || "bg-slate-500/20";
}
