import type { ReactNode } from "react";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { containerStyles, contentStyles, formWrapperStyles } from "./PanelLayout.styles";

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

  const combinedContentClass = `${contentStyles} ${contentClassName}`.trim();

  if (contentRole === "log") {
    contentElement = (
      <div
        className={combinedContentClass}
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
        className={combinedContentClass}
        aria-label={contentAriaLabel}
        aria-live={contentAriaLive}
      >
        {children}
      </section>
    );
  } else {
    contentElement = (
      <div className={combinedContentClass} aria-live={contentAriaLive}>
        {children}
      </div>
    );
  }

  return (
    <Card className={`fade-in ${containerStyles} ${className}`.trim()}>
      <CardHeader>{header}</CardHeader>
      {contentElement}
      <div className={formWrapperStyles}>{form}</div>
    </Card>
  );
}
