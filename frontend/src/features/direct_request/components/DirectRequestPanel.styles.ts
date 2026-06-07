import { css } from "@/styled-system/css";

export const titleStyles = css({
  fontSize: "15px",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "0.01em",
});

export const subtitleStyles = css({
  fontSize: "12px",
  color: "textSecondary",
  marginTop: "2px",
});

export const requestFormStyles = css({
  padding: "12px 16px",
  background: "panelBg",
});

export const formGridStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "10px",
});

export const inputGroupStyles = css({
  display: "flex",
  gap: "8px",
  overflow: "hidden",
  minWidth: "0",
});

export const selectRecipientStyles = css({
  flex: "0 0 auto",
  width: "160px!",
  borderRadius: "control",
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  height: "42px",
  color: "textPrimary",
  fontSize: "14px",
  padding: "0 36px 0 12px",
  appearance: "none",
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%235F6368' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "right 10px center",
  _focus: {
    borderColor: "primary",
    boxShadow: "focus",
    outline: "none",
  },
});

export const inputTaskStyles = css({
  flex: "1",
  minWidth: "0",
  width: "auto!",
  borderRadius: "control",
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  height: "42px",
  color: "textPrimary",
  fontSize: "14px",
  padding: "0 16px",
  _focus: {
    borderColor: "primary",
    boxShadow: "focus",
    outline: "none",
  },
});

export const submitButtonStyles = css({
  fontSize: "14px",
  height: "42px",
  borderRadius: "control",
  fontWeight: 500,
  letterSpacing: "0.01em",
  width: "100%",
});

export const requestListStyles = css({
  display: "flex",
  flexDirection: "column",
  background: "bg",
});

export const emptyStateStyles = css({
  textAlign: "center",
  color: "textMuted",
  padding: "48px 20px",
  fontSize: "14px",
  lineHeight: 1.6,
});

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
});

export const actionButtonStyles = css({
  fontSize: "13px",
  padding: "8px 0",
  flex: 1,
  borderRadius: "control",
  fontWeight: 500,
});

export const completeButtonStyles = css({
  background: "success!",
  color: "white!",
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
