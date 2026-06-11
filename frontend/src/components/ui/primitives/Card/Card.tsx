import type { ReactNode } from "react";
import {
  cardStyles,
  contentStyles,
  headerStyles,
  hoverableStyles,
} from "./Card.styles";

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
