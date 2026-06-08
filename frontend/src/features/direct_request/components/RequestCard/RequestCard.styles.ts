import { css } from "@/styled-system/css";

export const requestItemStyles = css({
  padding: "16px 20px",
  borderBottom: "1px solid",
  borderBottomColor: "border.divider",
  background: "panelBg",
  transition: "background 0.15s ease",
  _hover: {
    background: "bg",
  },
});

export const itemHeaderStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  marginBottom: "8px",
});

export const metaInfoStyles = css({
  display: "flex",
  gap: "6px",
  alignItems: "center",
  flexWrap: "wrap",
});

export const senderNameStyles = css({
  fontSize: "13px",
  fontWeight: 500,
  color: "textPrimary",
});

export const separatorStyles = css({
  color: "border.muted",
  fontSize: "12px",
});

export const timestampStyles = css({
  fontSize: "12px",
  color: "textMuted",
});

export const requestTextStyles = css({
  fontSize: "14px",
  lineHeight: 1.65,
  marginBottom: "0",
  color: "textBody",
  wordBreak: "break-word",
});

export const actionGroupStyles = css({
  display: "flex",
  gap: "8px",
  marginTop: "12px",
  "& button": {
    flex: 1,
  },
});

export const resolvedNoteStyles = css({
  fontSize: "11px",
  color: "success",
  fontWeight: 500,
  marginTop: "8px",
  display: "flex",
  alignItems: "center",
  gap: "4px",
});

export const requestPendingStyles = css({
  opacity: 0.5,
});
