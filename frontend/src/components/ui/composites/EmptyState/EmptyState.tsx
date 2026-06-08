import { emptyStateStyles } from "./EmptyState.styles";

interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return <div className={emptyStateStyles}>{message}</div>;
}
