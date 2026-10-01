"use client";

import { Navbar } from "./Navbar";
import { NotificationToast } from "./NotificationToast";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen cyber-grid">
      <Navbar />
      <main className="pt-16">{children}</main>
      <NotificationToast />
    </div>
  );
}
