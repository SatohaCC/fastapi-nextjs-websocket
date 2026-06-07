import type { SelectHTMLAttributes } from "react";
import {
  Input as RACInput,
  type InputProps as RACInputProps,
} from "react-aria-components";
import { inputStyles, selectStyles } from "./Input.styles";

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
