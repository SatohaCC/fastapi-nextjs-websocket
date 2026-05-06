import type { ReactNode } from "react";
import styles from "./Badge.module.css";

interface BadgeProps {
  variant?:
    | "requested"
    | "processing"
    | "completed"
    | "error"
    | "warning"
    | "default";
  children: ReactNode;
  className?: string;
}

export function Badge({
  variant = "default",
  children,
  className = "",
}: BadgeProps) {
  const combinedClassName =
    `${styles.base} ${styles[variant]} ${className}`.trim();

  return <span className={combinedClassName}>{children}</span>;
}
