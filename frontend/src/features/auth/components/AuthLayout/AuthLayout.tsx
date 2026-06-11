import type { FormEvent, ReactNode } from "react";
import {
  containerStyles,
  errorBoxStyles,
  formStyles,
  headerStyles,
  logoStyles,
  subtitleStyles,
} from "./AuthLayout.styles";

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return <div className={containerStyles}>{children}</div>;
}

interface AuthFormProps {
  children: ReactNode;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

export function AuthForm({ children, onSubmit }: AuthFormProps) {
  return (
    <form onSubmit={onSubmit} className={`fade-in ${formStyles}`}>
      {children}
    </form>
  );
}

export function AuthHeader({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <div className={headerStyles}>
      <h1 className={logoStyles}>{title}</h1>
      <p className={subtitleStyles}>{subtitle}</p>
    </div>
  );
}

export function AuthError({ message }: { message: string }) {
  return (
    <div className={errorBoxStyles} role="alert" aria-live="assertive">
      {message}
    </div>
  );
}
