"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/lib/store";

export function NotificationToast() {
  const notifications = useAppStore((s) => s.notifications);

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {notifications.map((n) => (
          <motion.div
            key={n.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className={`px-4 py-3 rounded-lg glass-card text-sm max-w-sm border ${
              n.type === "danger"
                ? "border-red-500/50"
                : n.type === "warning"
                ? "border-yellow-500/50"
                : "border-sky-500/50"
            }`}
          >
            {n.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
