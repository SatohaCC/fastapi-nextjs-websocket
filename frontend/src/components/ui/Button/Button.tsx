import {
  Button as RACButton,
  type ButtonProps as RACButtonProps,
} from "react-aria-components";
import { buttonStyles } from "./Button.styles";

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
