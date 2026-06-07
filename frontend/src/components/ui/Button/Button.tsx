import {
  Button as RACButton,
  type ButtonProps as RACButtonProps,
} from "react-aria-components";
import { cva } from "@/styled-system/css";

const buttonStyles = cva({
  base: {
    padding: "10px 24px",
    borderRadius: "9999px",
    fontWeight: 700,
    border: "none",
    cursor: "pointer",
    transition: "background 0.2s, opacity 0.2s",
    fontSize: "15px",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    outline: "none",
    "&[data-disabled]": {
      opacity: 0.5,
      cursor: "not-allowed",
    },
  },
  variants: {
    variant: {
      primary: {
        bg: "primary",
        color: "white",
        "&[data-hovered]": {
          bg: "primaryHover",
        },
      },
      secondary: {
        bg: "transparent",
        border: "1px solid",
        borderColor: "panelBorder",
        color: "white",
        padding: "8px 16px",
        fontSize: "14px",
        "&[data-hovered]": {
          bg: "rgba(255, 255, 255, 0.1)",
        },
      },
      ghost: {
        bg: "transparent",
        border: "1px solid transparent",
        color: "white",
        padding: "8px 16px",
        fontSize: "14px",
        "&[data-hovered]": {
          bg: "rgba(255, 255, 255, 0.05)",
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
        fontSize: "15px",
      },
      lg: {
        padding: "14px 32px",
        fontSize: "18px",
      },
    },
  },
});

interface ButtonProps extends RACButtonProps {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
  disabled?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <RACButton
      isDisabled={disabled ?? props.isDisabled}
      className={(state) => {
        const baseClass = buttonStyles({ variant, size });
        const customClass =
          typeof className === "function" ? className(state) : className;
        return `${baseClass} ${customClass}`.trim();
      }}
      {...props}
    >
      {children}
    </RACButton>
  );
}
