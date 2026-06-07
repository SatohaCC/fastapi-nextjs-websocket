import { css } from "@/styled-system/css";

export const containerStyles = css({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  background: "black",
  overflow: "hidden",
});

export const formStyles = css({
  padding: "32px",
  width: "100%",
  maxWidth: "360px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
});

export const headerStyles = css({
  textAlign: "center",
  marginBottom: "4px",
});

export const logoStyles = css({
  fontSize: "22px",
  fontWeight: 900,
  color: "white",
});

export const subtitleStyles = css({
  fontSize: "14px",
  color: "textSecondary",
  marginTop: "8px",
});

export const accountsStyles = css({
  border: "1px solid",
  borderColor: "panelBorder",
  borderRadius: "8px",
  overflow: "hidden",
});

export const accountsLabelStyles = css({
  fontSize: "11px",
  color: "textSecondary",
  padding: "7px 12px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
});

export const accountItemStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "8px 12px",
  width: "100%",
  background: "transparent",
  border: "none",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
  color: "white",
  cursor: "pointer",
  fontSize: "13px",
  transition: "background 0.15s",
  textAlign: "left",
  _last: {
    borderBottom: "none",
  },
  _hover: {
    background: "rgba(255, 255, 255, 0.05)",
  },
});

export const accountItemActiveStyles = css({
  background: "rgba(29, 155, 240, 0.12)!",
  borderLeft: "2px solid",
  borderLeftColor: "primary",
  paddingLeft: "10px",
});

export const accountNameStyles = css({
  fontWeight: 700,
});

export const accountPasswordStyles = css({
  fontSize: "12px",
  color: "textSecondary",
  fontFamily: "monospace",
});

export const errorBoxStyles = css({
  padding: "12px",
  background: "rgba(244, 33, 46, 0.1)",
  color: "error",
  borderRadius: "4px",
  fontSize: "13px",
  textAlign: "center",
  border: "1px solid rgba(244, 33, 46, 0.2)",
});

export const fieldGroupStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "4px",
});

export const inputStyles = css({
  padding: "12px 16px",
  fontSize: "14px",
});

export const submitButtonStyles = css({
  padding: "12px",
  fontSize: "15px",
  width: "100%",
});
