import type { InputHTMLAttributes, SelectHTMLAttributes } from "react";
import styles from "./Input.module.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className = "", ...props }: InputProps) {
  return <input className={`${styles.base} ${className}`.trim()} {...props} />;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
}

export function Select({ className = "", children, ...props }: SelectProps) {
  return (
    <select className={`${styles.base} ${className}`.trim()} {...props}>
      {children}
    </select>
  );
}
