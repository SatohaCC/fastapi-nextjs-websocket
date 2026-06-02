import type { InputHTMLAttributes, SelectHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className = "", ...props }: InputProps) {
  return <input className={`input-base ${className}`.trim()} {...props} />;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
}

export function Select({ className = "", children, ...props }: SelectProps) {
  return (
    <select className={`select-base ${className}`.trim()} {...props}>
      {children}
    </select>
  );
}
