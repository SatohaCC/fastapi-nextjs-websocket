"use client";

import { Loading } from "@/components/ui/primitives";

export interface WorkspaceLoadingProps {
  message?: string;
}

export function WorkspaceLoading({
  message = "Initializing App...",
}: WorkspaceLoadingProps) {
  return <Loading message={message} />;
}
