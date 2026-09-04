"use client";

import { useEffect, useState } from "react";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

let toastQueue: Array<(t: Toast) => void> = [];

export type ToastOptions =
  | string
  | { title: string; description?: string; variant?: "default" | "destructive" | "success" | string };

export function toast(options: ToastOptions, type: Toast["type"] = "info") {
  let message = "";
  let resolvedType: Toast["type"] = type;

  if (typeof options === "string") {
    message = options;
  } else {
    message = options.description ? `${options.title} - ${options.description}` : options.title;
    if (options.variant === "destructive") {
      resolvedType = "error";
    } else if (options.variant === "success") {
      resolvedType = "success";
    }
  }

  toastQueue.forEach(fn => fn({ id: Date.now().toString() + Math.random().toString(), message, type: resolvedType }));
}

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handler = (t: Toast) => {
      setToasts(prev => [...prev, t]);
      setTimeout(() => {
        setToasts(prev => prev.filter(x => x.id !== t.id));
      }, 3500);
    };
    toastQueue.push(handler);
    return () => { toastQueue = toastQueue.filter(fn => fn !== handler); };
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`glass px-4 py-3 rounded-xl border text-sm animate-slide-in flex items-center gap-2 ${
            t.type === "success" ? "border-emerald-500/30 text-emerald-400" :
            t.type === "error" ? "border-rose-500/30 text-rose-400" :
            "border-primary/30 text-primary"
          }`}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
