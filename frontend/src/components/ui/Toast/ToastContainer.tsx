"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { type ToastItem, toast } from "@/lib/toast";
import { css } from "@/styled-system/css";
import { Toast } from "./Toast";

const containerStyles = css({
  position: "fixed",
  top: "1rem",
  right: "1rem",
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
  zIndex: 9999,
  pointerEvents: "none",
});

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
