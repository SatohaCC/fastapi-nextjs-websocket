import {
  Button as RACButton,
  type ButtonProps as RACButtonProps,
} from "react-aria-components";
import { buttonStyles } from "./Button.styles";

interface ButtonProps extends RACButtonProps {
  variant?: "primary" | "secondary" | "ghost" | "success";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  children: React.ReactNode;
  disabled?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <RACButton
      isDisabled={disabled ?? props.isDisabled}
      className={(state) => {
        const baseClass = buttonStyles({ variant, size, fullWidth });
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
