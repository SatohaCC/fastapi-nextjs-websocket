import type { ReactNode } from "react";
import { badgeStyles } from "./Badge.styles";

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
  return (
    <span className={`${badgeStyles({ variant })} ${className}`.trim()}>
      {children}
    </span>
  );
}

