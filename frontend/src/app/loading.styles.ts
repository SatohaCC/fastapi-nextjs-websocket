import { css } from "@/styled-system/css";

export const containerStyles = css({
  height: "100vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: "16px",
  background: "bg",
});

export const logoStyles = css({
  fontSize: "4xl",
  fontWeight: 900,
  animation: "pulse 2s infinite ease-in-out",
});

export const trackStyles = css({
  width: "200px",
  height: "2px",
  background: "surface.subtle",
  borderRadius: "full",
  overflow: "hidden",
  position: "relative",
});

export const barStyles = css({
  position: "absolute",
  top: 0,
  left: 0,
  width: "50%",
  height: "100%",
  background: "primary",
  boxShadow: "0 0 15px {colors.primary}",
  animation: "shimmer 1.5s infinite ease-in-out",
});

export const captionStyles = css({
  fontSize: "xs",
  color: "textSecondary",
  fontFamily: "monospace",
  textTransform: "uppercase",
  letterSpacing: "0.1em",
});
