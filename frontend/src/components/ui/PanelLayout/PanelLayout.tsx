import type { ReactNode } from "react";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import styles from "./PanelLayout.module.css";

interface PanelLayoutProps {
  header: ReactNode;
  form: ReactNode;
  children: ReactNode;
  contentClassName?: string;
  className?: string;
  contentRole?: "log" | "region" | "navigation" | "search" | "main" | "form";
  contentAriaLabel?: string;
  contentAriaLive?: "polite" | "assertive" | "off";
}

export function PanelLayout({
  header,
  form,
  children,
  contentClassName = "",
  className = "",
  contentRole,
  contentAriaLabel,
  contentAriaLive,
}: PanelLayoutProps) {
  let contentElement: ReactNode;

  if (contentRole === "log") {
    contentElement = (
      <div
        className={`${styles.content} ${contentClassName}`.trim()}
        role="log"
        aria-label={contentAriaLabel}
        aria-live={contentAriaLive}
      >
        {children}
      </div>
    );
  } else if (contentRole === "region") {
    contentElement = (
      <section
        className={`${styles.content} ${contentClassName}`.trim()}
        aria-label={contentAriaLabel}
        aria-live={contentAriaLive}
      >
        {children}
      </section>
    );
  } else {
    contentElement = (
      <div
        className={`${styles.content} ${contentClassName}`.trim()}
        aria-live={contentAriaLive}
      >
        {children}
      </div>
    );
  }

  return (
    <Card className={`fade-in ${styles.container} ${className}`.trim()}>
      <CardHeader>{header}</CardHeader>
      {contentElement}
      <div className={styles.formWrapper}>{form}</div>
    </Card>
  );
}
