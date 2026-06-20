import type { ReactNode } from "react";
import {
  containerStyles,
  errorToastStyles,
  mainStyles,
} from "./WorkspaceLayout.styles";

interface WorkspaceLayoutProps {
  header?: ReactNode;
  presence?: ReactNode;
  footer: ReactNode;
  error?: string | null;
  children: ReactNode;
}

export function WorkspaceLayout({
  header,
  presence,
  footer,
  error,
  children,
}: WorkspaceLayoutProps) {
  return (
    <div className={containerStyles}>
      {header}

      {presence}

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
