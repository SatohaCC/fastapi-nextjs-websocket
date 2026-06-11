import { loadingContainerStyles } from "./Loading.styles";

interface LoadingProps {
  message?: string;
}

export function Loading({ message = "LOADING..." }: LoadingProps) {
  return (
    <div className={loadingContainerStyles} role="alert" aria-busy="true">
      {message}
    </div>
  );
}
