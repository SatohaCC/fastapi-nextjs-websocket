import { css } from "@/styled-system/css";

const footerStyles = css({
  textAlign: "center",
  padding: "8px 0",
});

const footerTextStyles = css({
  fontSize: "11px",
  color: "textSecondary",
  letterSpacing: "0.02em",
});

export function WorkspaceFooter() {
  return (
    <footer className={footerStyles}>
      <p className={footerTextStyles}>
        &copy; 2026 Satoha. All rights reserved.
      </p>
    </footer>
  );
}
