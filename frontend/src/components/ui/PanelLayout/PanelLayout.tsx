import type { ReactNode } from "react";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { css } from "@/styled-system/css";

const containerStyles = css({
  gridRow: "span 3",
  display: "grid",
  gridTemplateRows: "subgrid",
  "@media (max-width: 1024px)": {
    gridRow: "unset",
    display: "flex",
    flexDirection: "column",
  },
});

const contentStyles = css({
  overflowY: "auto",
  minHeight: 0,
  "@media (max-width: 1024px)": {
    flex: 1,
  },
});

const formWrapperStyles = css({
  borderTop: "1px solid",
  borderColor: "panelBorder",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
});

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
