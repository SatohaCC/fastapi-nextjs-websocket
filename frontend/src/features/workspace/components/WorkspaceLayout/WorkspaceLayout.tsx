import type { ReactNode } from "react";
import {
  containerStyles,
  errorToastStyles,
  mainStyles,
} from "./WorkspaceLayout.styles";

interface WorkspaceLayoutProps {
  header: ReactNode;
  footer: ReactNode;
  error?: string | null;
  children: ReactNode;
}

export function WorkspaceLayout({
  header,
  footer,
  error,
  children,
}: WorkspaceLayoutProps) {
  return (
    <div className={containerStyles}>
      {header}

      {error && (
        <div className={`fade-in ${errorToastStyles}`}>
          System Alert: {error}
        </div>
      )}

      <main className={mainStyles}>{children}</main>

      {footer}
    </div>
  );
}
