import { footerStyles, footerTextStyles } from "./WorkspaceFooter.styles";

export function WorkspaceFooter() {
  return (
    <footer className={footerStyles}>
      <p className={footerTextStyles}>
        &copy; {new Date().getFullYear()} WebSocket test app.
      </p>
    </footer>
  );
}
