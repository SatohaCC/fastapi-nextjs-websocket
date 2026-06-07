"use client";

import type { ToastItem } from "@/lib/toast";
import { css } from "@/styled-system/css";

const toastStyles = css({
  display: "flex",
  alignItems: "flex-start",
  gap: "12px",
  padding: "12px 16px",
  borderRadius: "12px",
  background: "#ffffff",
  border: "1px solid rgba(0, 0, 0, 0.08)",
  boxShadow: "0 4px 16px rgba(0, 0, 0, 0.12)",
  minWidth: "240px",
  maxWidth: "360px",
  pointerEvents: "auto",
  animation: "fadeIn 0.3s ease-out forwards",
});

const leavingStyles = css({
  animation: "fadeOut 0.25s ease-in forwards",
});

const bodyStyles = css({
  flex: 1,
  minWidth: 0,
});

const titleStyles = css({
  fontSize: "0.875rem",
  fontWeight: 500,
  color: "#0f1419",
  lineHeight: 1.4,
  wordBreak: "break-word",
});

const descriptionStyles = css({
  fontSize: "0.8rem",
  color: "#536471",
  marginTop: "2px",
  lineHeight: 1.4,
  wordBreak: "break-word",
});

const closeStyles = css({
  flexShrink: 0,
  background: "none",
  border: "none",
  color: "#536471",
  cursor: "pointer",
  fontSize: "1rem",
  lineHeight: 1,
  padding: 0,
  transition: "color 0.15s",
  _hover: {
    color: "#0f1419",
  },
});

interface ToastProps extends ToastItem {
  onClose: (id: string) => void;
}

export function Toast({
  id,
  title,
  description,
  leaving,
  onClose,
}: ToastProps) {
  return (
    <output
      aria-live="polite"
      className={`${toastStyles} ${leaving ? leavingStyles : ""}`.trim()}
    >
      <div className={bodyStyles}>
        <p className={titleStyles}>{title}</p>
        {description && <p className={descriptionStyles}>{description}</p>}
      </div>
      <button
        className={closeStyles}
        onClick={() => onClose(id)}
        aria-label="閉じる"
        type="button"
      >
        ×
      </button>
    </output>
  );
}
