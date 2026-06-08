"use client";

import { Loading } from "@/components/ui/Loading/Loading";

export interface WorkspaceLoadingProps {
  message?: string;
}

export function WorkspaceLoading({
  message = "Initializing App...",
}: WorkspaceLoadingProps) {
  return <Loading message={message} />;
}
