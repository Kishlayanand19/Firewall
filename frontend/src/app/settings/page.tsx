"use client";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { getPublicApiDisplayUrl } from "@/lib/env";
import { useAppStore } from "@/lib/store";
import { Moon, Sun, Bell, Key, Database } from "lucide-react";

export default function SettingsPage() {
  const { theme, toggleTheme } = useAppStore();

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold gradient-text mb-8">Settings</h1>

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {theme === "dark" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
              Appearance
            </CardTitle>
          </CardHeader>
          <button
            onClick={toggleTheme}
            className="w-full p-3 rounded-lg border border-sky-500/30 hover:bg-sky-500/10 transition-colors text-sm"
          >
            Switch to {theme === "dark" ? "Light" : "Dark"} Mode
          </button>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
          </CardHeader>
          <p className="text-sm text-slate-400">Real-time threat alerts enabled for dangerous content.</p>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              API Configuration
            </CardTitle>
          </CardHeader>
          <p className="text-sm text-slate-400">
            API endpoint: {getPublicApiDisplayUrl()}
          </p>
          <p className="text-xs text-slate-500 mt-2">
            AI keys are configured on the server only — never in the browser.
          </p>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Data Retention
            </CardTitle>
          </CardHeader>
          <p className="text-sm text-slate-400">Analysis history stored in PostgreSQL when database is connected.</p>
        </Card>
      </div>
    </div>
  );
}
