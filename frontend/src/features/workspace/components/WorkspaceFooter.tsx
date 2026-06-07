import { footerStyles, footerTextStyles } from "./WorkspaceFooter.styles";

export function WorkspaceFooter() {
  return (
    <footer className={footerStyles}>
      <p className={footerTextStyles}>
        &copy; 2026 Satoha. All rights reserved.
      </p>
    </footer>
  );
}
