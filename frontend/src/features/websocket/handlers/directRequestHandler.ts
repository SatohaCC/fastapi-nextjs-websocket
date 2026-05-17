import { mergeById } from "@/features/websocket/utils/mergeById";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
} from "@/types/ws";
import type { HandlerDeps } from "./types";

export function handleDirectRequestMessage(
  data: DirectRequestServerMessage,
  deps: HandlerDeps,
): void {
  deps.setRequestMessages((prev) => {
    if (prev.some((r) => r.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}

export function handleDirectRequestUpdated(
  data: DirectRequestUpdatedServerMessage,
  deps: HandlerDeps,
): void {
  deps.setRequestMessages((prev) =>
    prev.map((r) =>
      r.id === data.id
        ? {
            ...r,
            status: data.status,
            updated_at: data.updated_at,
            seq: data.seq,
          }
        : r,
    ),
  );
}
