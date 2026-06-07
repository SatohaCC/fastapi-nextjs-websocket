import type { ReactNode } from "react";
import { css } from "@/styled-system/css";

const cardStyles = css({
  background: "rgba(18, 18, 23, 0.7)",
  backdropFilter: "blur(12px) saturate(180%)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "16px",
  overflow: "hidden",
  boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
});

const hoverableStyles = css({
  transition: "background 0.2s",
  _hover: {
    background: "rgba(255, 255, 255, 0.03)",
  },
});

const headerStyles = css({
  padding: "16px 20px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
});

const contentStyles = css({
  padding: "20px",
});

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
  const combinedClass =
    `${cardStyles} ${hoverable ? hoverableStyles : ""} ${className}`.trim();
  return <div className={combinedClass}>{children}</div>;
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = "" }: CardHeaderProps) {
  return (
    <div className={`${headerStyles} ${className}`.trim()}>{children}</div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return (
    <div className={`${contentStyles} ${className}`.trim()}>{children}</div>
  );
}
