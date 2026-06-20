import { css } from "@/styled-system/css";

export const settingsPanelStyles = css({
  width: "100%",
  maxWidth: "540px",
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "panel",
  padding: "24px",
  boxShadow: "modal",
  display: "flex",
  flexDirection: "column",
  animation: "fadeIn 0.15s ease-out",
});

export const settingsPageWrapperStyles = css({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  minHeight: "calc(100vh - 64px)",
  background: "bg",
  padding: "24px 20px",
});

export const settingsHeaderStyles = css({
  width: "100%",
  maxWidth: "540px",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "24px",
});

export const settingsPageTitleStyles = css({
  fontSize: "20px",
  fontWeight: 600,
  color: "textPrimary",
});

export const backButtonStyles = css({
  padding: "8px 16px",
  borderRadius: "6px",
  background: "panelBg",
  color: "textSecondary",
  border: "1px solid",
  borderColor: "border.default",
  fontSize: "13px",
  fontWeight: 500,
  cursor: "pointer",
  transition: "all 0.15s ease",
  "&:hover": {
    color: "textPrimary",
    borderColor: "border.muted",
    background: "surface.subtle",
  },
});

export const settingsTitleStyles = css({
  fontSize: "11px",
  fontWeight: 600,
  color: "textSecondary",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: "12px",
  paddingLeft: "4px",
});

export const settingsListStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "4px",
});

export const sectionSeparatorStyles = css({
  borderTop: "1px solid",
  borderColor: "border.default",
  margin: "16px 0",
});

export const formSectionStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  marginBottom: "16px",
});

export const formRowStyles = css({
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

export const sectionTitleStyles = css({
  fontSize: "12px",
  fontWeight: 600,
  color: "textPrimary",
  marginBottom: "8px",
});

export const linkButtonStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  width: "100%",
  padding: "12px 16px",
  borderRadius: "8px",
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  color: "textPrimary",
  fontSize: "14px",
  fontWeight: 500,
  cursor: "pointer",
  textDecoration: "none",
  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    background: "surface.subtle",
    borderColor: "border.muted",
    paddingLeft: "20px", // Micro-animation: slide text slightly on hover
  },
});

export const dangerLinkStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  width: "100%",
  padding: "12px 16px",
  borderRadius: "8px",
  background: "rgba(239, 68, 68, 0.05)",
  border: "1px solid rgba(239, 68, 68, 0.1)",
  color: "rgb(239, 68, 68)",
  fontSize: "14px",
  fontWeight: 500,
  cursor: "pointer",
  textDecoration: "none",
  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    background: "rgba(239, 68, 68, 0.1)",
    borderColor: "rgba(239, 68, 68, 0.2)",
    paddingLeft: "20px",
  },
});

export const inlineButtonStyles = css({
  padding: "6px 12px",
  borderRadius: "6px",
  background: "rgba(99, 102, 241, 0.1)",
  color: "rgb(99, 102, 241)",
  border: "1px solid rgba(99, 102, 241, 0.2)",
  fontSize: "12px",
  fontWeight: 600,
  cursor: "pointer",
  transition: "all 0.15s ease",
  "&:hover": {
    background: "rgba(99, 102, 241, 0.2)",
  },
  "&:disabled": {
    opacity: 0.5,
    cursor: "not-allowed",
  },
});

export const dangerButtonStyles = css({
  width: "100%",
  padding: "8px 12px",
  borderRadius: "6px",
  background: "rgba(239, 68, 68, 0.1)",
  color: "rgb(239, 68, 68)",
  border: "1px solid rgba(239, 68, 68, 0.2)",
  fontSize: "12px",
  fontWeight: 600,
  cursor: "pointer",
  textAlign: "center",
  transition: "all 0.15s ease",
  "&:hover": {
    background: "rgba(239, 68, 68, 0.2)",
  },
  "&:disabled": {
    opacity: 0.5,
    cursor: "not-allowed",
  },
});

export const statusTextStyles = css({
  fontSize: "11px",
  marginTop: "4px",
  fontWeight: 500,
});

export const errorTextStyles = css({
  color: "error",
});

export const successTextStyles = css({
  color: "rgba(16, 185, 129, 1)",
});

export const readOnlyFieldStyles = css({
  fontSize: "13px",
  color: "textSecondary",
  background: "rgba(255, 255, 255, 0.05)",
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "6px",
  padding: "8px 12px",
  width: "100%",
  marginBottom: "12px",
});
