import { css } from "@/styled-system/css";

export const switchStyles = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: "12px",
  padding: "10px 12px",
  borderRadius: "control",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  userSelect: "none",
  transition: "background 0.15s",
  "&[data-hovered]": {
    background: "surface.subtle",
  },
  "&[data-focus-visible]": {
    outlineWidth: "2px",
    outlineStyle: "solid",
    outlineColor: "primary",
    outlineOffset: "1px",
  },
});

export const labelStyles = css({
  fontSize: "14px",
  fontWeight: 400,
  color: "textPrimary",
  flex: 1,
  textAlign: "left",
  whiteSpace: "nowrap",
});

export const trackStyles = css({
  position: "relative",
  flexShrink: 0,
  width: "40px",
  height: "22px",
  borderRadius: "full",
  background: "border.muted",
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
  width: "18px",
  height: "18px",
  borderRadius: "full",
  background: "white",
  boxShadow: "thumb",
  transition: "transform 0.2s",
  "&[data-selected]": {
    transform: "translateX(18px)",
  },
});
