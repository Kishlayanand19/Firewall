"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Moon, Sun, Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analyzer", label: "Live Analyzer" },
  { href: "/feed", label: "Feed Sim" },
  { href: "/agents", label: "AI Agents" },
  { href: "/threat-intel", label: "Threat Intel" },
  { href: "/api-docs", label: "API" },
];

export function Navbar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useAppStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isLanding = pathname === "/";

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-sky-500/20 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <Shield className="h-8 w-8 text-sky-400" />
          <span className="font-bold">
            <span className="gradient-text">Thought Firewall</span>
          </span>
        </Link>

        {!isLanding && (
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "px-3 py-2 rounded-lg text-sm transition-colors",
                  pathname === link.href
                    ? "bg-sky-500/20 text-sky-300"
                    : "text-slate-400 hover:text-sky-300 hover:bg-white/5"
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          {isLanding ? (
            <>
              <Link href="/dashboard" className="hidden sm:block">
                <Button variant="outline" size="sm">Dashboard</Button>
              </Link>
              <Link href="/analyzer">
                <Button size="sm">Start Scanning</Button>
              </Link>
            </>
          ) : (
            <Link href="/settings">
              <Button variant="outline" size="sm">Settings</Button>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X /> : <Menu />}
          </Button>
        </div>
      </div>

      {mobileOpen && !isLanding && (
        <div className="md:hidden border-t border-sky-500/20 bg-background/95 p-4 space-y-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "block px-3 py-2 rounded-lg text-sm",
                pathname === link.href ? "bg-sky-500/20 text-sky-300" : "text-slate-400"
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
