"use client";

import type { ToastItem } from "@/lib/toast";
import styles from "./Toast.module.css";

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
      className={`${styles.toast} ${leaving ? styles.leaving : ""}`}
    >
      <div className={styles.body}>
        <p className={styles.title}>{title}</p>
        {description && <p className={styles.description}>{description}</p>}
      </div>
      <button
        className={styles.close}
        onClick={() => onClose(id)}
        aria-label="閉じる"
        type="button"
      >
        ×
      </button>
    </output>
  );
}
