import type { ReactNode } from "react";
import styles from "./Card.module.css";

interface CardProps {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
}

export function Card({
  children,
  className = "",
  hoverable = false,
}: CardProps) {
  return (
    <div
      className={`${styles.base} ${hoverable ? styles.hoverable : ""} ${className}`.trim()}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = "" }: CardHeaderProps) {
  return (
    <div className={`${styles.header} ${className}`.trim()}>{children}</div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return (
    <div className={`${styles.content} ${className}`.trim()}>{children}</div>
  );
}
