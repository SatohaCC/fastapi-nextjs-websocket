import { cva } from "@/styled-system/css";

export const buttonStyles = cva({
  base: {
    padding: "10px 24px",
    borderRadius: "control",
    fontWeight: 500,
    border: "none",
    cursor: "pointer",
    transition: "background 0.2s, box-shadow 0.2s, transform 0.1s ease",
    fontSize: "14px",
    letterSpacing: "0.01em",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    outline: "none",
    "&[data-focus-visible]": {
      outlineWidth: "3px",
      outlineStyle: "solid",
      outlineColor: "primary",
      outlineOffset: "3px",
      boxShadow: "focusOuter!",
    },
    "&[data-disabled]": {
      background: "disabled.bg!",
      color: "textMuted!",
      boxShadow: "none!",
      border: "1px solid",
      borderColor: "panelBorder!",
      cursor: "not-allowed",
    },
    _active: {
      transform: "scale(0.99)",
    },
  },
  variants: {
    variant: {
      primary: {
        bg: "primary",
        color: "white",
        boxShadow: "buttonDefault",
        "&[data-hovered]": {
          bg: "primaryHover",
          boxShadow: "buttonHover",
        },
      },
      secondary: {
        bg: "panelBg",
        border: "1px solid",
        borderColor: "panelBorder",
        color: "primary",
        padding: "8px 16px",
        fontSize: "14px",
        "&[data-hovered]": {
          bg: "surface.active",
        },
      },
      ghost: {
        bg: "transparent",
        border: "1px solid transparent",
        color: "primary",
        padding: "8px 16px",
        fontSize: "14px",
        "&[data-hovered]": {
          bg: "surface.active",
        },
      },
      success: {
        bg: "success",
        color: "white",
        boxShadow: "buttonDefault",
        "&[data-hovered]": {
          opacity: 0.9,
          boxShadow: "buttonHover",
        },
      },
    },
    size: {
      sm: {
        padding: "6px 16px",
        fontSize: "13px",
      },
      md: {
        padding: "10px 24px",
        fontSize: "14px",
      },
      lg: {
        padding: "14px 32px",
        fontSize: "16px",
      },
    },
    fullWidth: {
      true: {
        width: "100%",
        display: "flex",
      },
      false: {
        display: "inline-flex",
      },
    },
  },
});
