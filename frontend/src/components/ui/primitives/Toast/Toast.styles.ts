import { css } from "@/styled-system/css";

export const containerStyles = css({
  position: "fixed",
  top: "1rem",
  right: "1rem",
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
  zIndex: 9999,
  pointerEvents: "none",
});

export const toastStyles = css({
  display: "flex",
  alignItems: "flex-start",
  gap: "12px",
  padding: "12px 16px",
  borderRadius: "panel",
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.overlay",
  boxShadow: "toast",
  minWidth: "240px",
  maxWidth: "360px",
  pointerEvents: "auto",
  animation: "fadeIn 0.3s ease-out forwards",
});

export const leavingStyles = css({
  animation: "fadeOut 0.25s ease-in forwards",
});

export const bodyStyles = css({
  flex: 1,
  minWidth: 0,
});

export const titleStyles = css({
  fontSize: "md",
  fontWeight: 500,
  color: "toast.text",
  lineHeight: 1.4,
  wordBreak: "break-word",
});

export const descriptionStyles = css({
  fontSize: "sm",
  color: "toast.subtext",
  marginTop: "2px",
  lineHeight: 1.4,
  wordBreak: "break-word",
});

export const closeStyles = css({
  flexShrink: 0,
  background: "none",
  border: "none",
  color: "toast.subtext",
  cursor: "pointer",
  fontSize: "lg",
  lineHeight: 1,
  padding: 0,
  transition: "color 0.15s",
  _hover: {
    color: "toast.text",
  },
});
