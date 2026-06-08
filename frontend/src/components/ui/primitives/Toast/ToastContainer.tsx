"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { type ToastItem, toast } from "@/lib/toast";
import { Toast } from "./Toast";
import { containerStyles } from "./Toast.styles";

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return toast.subscribe(setToasts);
  }, []);

  if (!mounted) return null;

  return createPortal(
    <div className={containerStyles}>
      {toasts.map((t) => (
        <Toast key={t.id} {...t} onClose={toast.dismiss} />
      ))}
    </div>,
    document.body,
  );
}
