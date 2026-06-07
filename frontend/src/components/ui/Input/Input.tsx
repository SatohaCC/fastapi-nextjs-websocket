import type { SelectHTMLAttributes } from "react";
import {
  Input as RACInput,
  type InputProps as RACInputProps,
} from "react-aria-components";
import { css } from "@/styled-system/css";

const inputStyles = css({
  background: "black",
  border: "1px solid",
  borderColor: "panelBorder",
  color: "white",
  padding: "12px 16px",
  borderRadius: "4px",
  width: "100%",
  fontSize: "16px",
  outline: "none",
  transition: "border-color 0.2s, box-shadow 0.2s",
  _focus: {
    borderColor: "primary",
    boxShadow: "0 0 0 2px {colors.primary}",
  },
});

const selectStyles = css({
  background: "black",
  border: "1px solid",
  borderColor: "panelBorder",
  color: "white",
  padding: "12px 16px",
  borderRadius: "4px",
  width: "100%",
  fontSize: "16px",
  outline: "none",
  transition: "border-color 0.2s, box-shadow 0.2s",
  appearance: "none",
  paddingRight: "40px",
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "right 13px center",
  _focus: {
    borderColor: "primary",
    boxShadow: "0 0 0 2px {colors.primary}",
  },
});

export function Input({ className = "", ...props }: RACInputProps) {
  return (
    <RACInput className={`${inputStyles} ${className}`.trim()} {...props} />
  );
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
}

export function Select({ className = "", children, ...props }: SelectProps) {
  return (
    <select className={`${selectStyles} ${className}`.trim()} {...props}>
      {children}
    </select>
  );
}
