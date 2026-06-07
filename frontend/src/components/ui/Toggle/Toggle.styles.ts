import { css } from "@/styled-system/css";

export const switchStyles = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "12px 16px",
  borderRadius: "8px",
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  cursor: "pointer",
  userSelect: "none",
});

export const labelStyles = css({
  fontSize: "15px",
  fontWeight: 500,
  color: "textPrimary",
});

export const trackStyles = css({
  position: "relative",
  width: "44px",
  height: "24px",
  borderRadius: "99px",
  background: "#2f3336",
  transition: "background 0.2s",
  display: "inline-block",
  "&[data-selected]": {
    background: "primary",
  },
});

export const thumbStyles = css({
  position: "absolute",
  top: "2px",
  left: "2px",
  width: "20px",
  height: "20px",
  borderRadius: "50%",
  background: "white",
  transition: "transform 0.2s",
  "&[data-selected]": {
    transform: "translateX(20px)",
  },
});
