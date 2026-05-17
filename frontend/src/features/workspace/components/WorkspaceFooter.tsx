import styles from "./WorkspaceFooter.module.css";

export function WorkspaceFooter() {
  return (
    <footer className={styles.footer}>
      <p className={styles.footerText}>
        &copy; 2026 Satoha. All rights reserved.
      </p>
    </footer>
  );
}
