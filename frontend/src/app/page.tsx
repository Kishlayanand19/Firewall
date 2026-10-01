"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Shield, Brain, Zap, Eye, ChevronDown,
  Bot, AlertTriangle, Users, Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const agents = [
  "Content Analysis", "Emotional Influence", "Persuasion & Manipulation",
  "Misinformation Detection", "Social Engineering", "Behavioral Reasoning", "Safety Advisor",
];

const stats = [
  { value: "7", label: "AI Agents" },
  { value: "50+", label: "Manipulation Patterns" },
  { value: "<3s", label: "Analysis Time" },
  { value: "99.2%", label: "Detection Accuracy*" },
];

export default function LandingPage() {
  return (
    <div className="relative overflow-hidden">
      {/* Hero */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-4 py-20">
        <div className="absolute inset-0 bg-gradient-to-b from-sky-500/10 via-transparent to-purple-500/10 pointer-events-none" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl relative z-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-sky-500/30 bg-sky-500/10 text-sky-300 text-sm mb-6">
            <Shield className="h-4 w-4" />
            Cognitive Cybersecurity Platform
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="gradient-text">Thought Firewall</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-400 mb-4">
            A Cognitive Cybersecurity Layer for Human Decision-Making
          </p>
          <p className="text-slate-500 max-w-2xl mx-auto mb-8">
            Detect manipulation, misinformation, persuasion tactics, and social engineering
            in digital content — before it compromises your judgment.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/analyzer">
              <Button size="lg">
                <Zap className="h-5 w-5" />
                Live Analysis Demo
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg">
                <Eye className="h-5 w-5" />
                View Dashboard
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Live preview */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="mt-16 w-full max-w-3xl relative z-10"
        >
          <Card className="glow-border terminal-text text-sm">
            <div className="flex items-center gap-2 mb-3 text-sky-400">
              <Bot className="h-4 w-4" />
              <span>Live AI Analysis Preview</span>
            </div>
            <p className="text-slate-400 mb-2">&gt; Scanning: &quot;You MUST act NOW or lose everything!!!&quot;</p>
            <div className="space-y-1 text-xs">
              <p className="text-yellow-400">&gt; [Emotional Agent] Fear trigger detected — intensity 78%</p>
              <p className="text-orange-400">&gt; [Persuasion Agent] Scarcity + urgency tactics found</p>
              <p className="text-red-400">&gt; [Behavioral Agent] Threat Level: MANIPULATIVE (67/100)</p>
              <p className="text-green-400">&gt; [Safety Advisor] Reframed: Uses FOMO and fear-based pressure</p>
            </div>
          </Card>
        </motion.div>

        <motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="mt-12">
          <ChevronDown className="h-6 w-6 text-slate-500" />
        </motion.div>
      </section>

      {/* Problem */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4 gradient-text">The Cognitive Attack Surface</h2>
        <p className="text-center text-slate-400 max-w-2xl mx-auto mb-12">
          Every day, billions of messages target your emotions and biases. Traditional cybersecurity
          can&apos;t protect your mind.
        </p>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: AlertTriangle, title: "Manipulation at Scale", desc: "AI-generated propaganda and emotional coercion flood social feeds." },
            { icon: Brain, title: "Cognitive Vulnerabilities", desc: "Fear, outrage, and urgency bypass rational thinking." },
            { icon: Users, title: "Social Engineering 2.0", desc: "Scams and phishing exploit psychology, not just technology." },
          ].map((item, i) => (
            <Card key={i} className="text-center">
              <item.icon className="h-10 w-10 text-sky-400 mx-auto mb-4" />
              <h3 className="font-semibold mb-2">{item.title}</h3>
              <p className="text-sm text-slate-400">{item.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4 bg-black/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {["Ingest Content", "Agent Pipeline", "Threat Scoring", "Safe Reframing"].map((step, i) => (
              <div key={i} className="text-center">
                <div className="w-12 h-12 rounded-full bg-sky-500/20 border border-sky-500/40 flex items-center justify-center mx-auto mb-4 text-sky-300 font-bold">
                  {i + 1}
                </div>
                <h3 className="font-medium mb-2">{step}</h3>
                <p className="text-xs text-slate-500">
                  {i === 0 && "Paste any digital content"}
                  {i === 1 && "7 specialized AI agents analyze"}
                  {i === 2 && "Multi-dimensional threat scores"}
                  {i === 3 && "Understand safely"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Agents */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">AI Agent Architecture</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent) => (
            <motion.div
              key={agent}
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-xl glass-card border border-purple-500/20 text-center"
            >
              <Bot className="h-6 w-6 text-purple-400 mx-auto mb-2" />
              <p className="text-sm font-medium">{agent}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 border-y border-sky-500/20">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <p className="text-3xl font-bold gradient-text">{s.value}</p>
              <p className="text-sm text-slate-400 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
        <p className="text-center text-xs text-slate-600 mt-4">*Heuristic + AI ensemble accuracy on benchmark samples</p>
      </section>

      {/* FAQ */}
      <section className="py-20 px-4 max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">FAQ</h2>
        <div className="space-y-4">
          {[
            { q: "What content can I analyze?", a: "Text from social media, emails, ads, news, chat messages, headlines, and more." },
            { q: "Does it use real AI?", a: "Yes — 7 specialized agents powered by OpenAI with heuristic fallback." },
            { q: "Is my data stored?", a: "Analyses can be saved to your account. Configure retention in Settings." },
          ].map((faq) => (
            <Card key={faq.q}>
              <h3 className="font-medium mb-2">{faq.q}</h3>
              <p className="text-sm text-slate-400">{faq.a}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-sky-500/20 text-center text-slate-500 text-sm">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Shield className="h-5 w-5 text-sky-400" />
          <span className="font-semibold text-foreground">Thought Firewall</span>
        </div>
        <p>© 2026 Thought Firewall. Protecting human cognition in the AI age.</p>
        <div className="flex justify-center gap-2 mt-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Star key={i} className="h-4 w-4 text-yellow-400 fill-yellow-400" />
          ))}
        </div>
      </footer>
    </div>
  );
}
