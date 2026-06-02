import type { ReactNode } from "react";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import styles from "./PanelLayout.module.css";

interface PanelLayoutProps {
  header: ReactNode;
  form: ReactNode;
  children: ReactNode;
  contentClassName?: string;
  className?: string;
}

export function PanelLayout({
  header,
  form,
  children,
  contentClassName = "",
  className = "",
}: PanelLayoutProps) {
  return (
    <Card className={`fade-in ${styles.container} ${className}`.trim()}>
      <CardHeader>{header}</CardHeader>
      <div className={`${styles.content} ${contentClassName}`.trim()}>
        {children}
      </div>
      <div className={styles.formWrapper}>{form}</div>
    </Card>
  );
}
