import type { ReactNode } from "react";
import { Card, CardHeader } from "@/components/ui/primitives/Card/Card";
import {
  containerStyles,
  contentStyles,
  formWrapperStyles,
} from "./PanelLayout.styles";

interface PanelLayoutProps {
  header: ReactNode;
  form: ReactNode;
  children: ReactNode;
  padding?: "none" | "normal";
  contentRole?: "log" | "region" | "navigation" | "search" | "main" | "form";
  contentAriaLabel?: string;
  contentAriaLive?: "polite" | "assertive" | "off";
  contentRef?: React.RefObject<HTMLDivElement | HTMLElement | null>;
}

export function PanelLayout({
  header,
  form,
  children,
  padding = "none",
  contentRole,
  contentAriaLabel,
  contentAriaLive,
  contentRef,
}: PanelLayoutProps) {
  let contentElement: ReactNode;

  const combinedContentClass = contentStyles({ padding });

  if (contentRole === "log") {
    contentElement = (
      <div
        className={combinedContentClass}
        role="log"
        aria-label={contentAriaLabel}
        aria-live={contentAriaLive}
        ref={contentRef as React.RefObject<HTMLDivElement | null>}
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
        ref={contentRef as React.RefObject<HTMLElement | null>}
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
    <Card className={`fade-in ${containerStyles}`.trim()}>
      <CardHeader>{header}</CardHeader>
      {contentElement}
      <div className={formWrapperStyles}>{form}</div>
    </Card>
  );
}
