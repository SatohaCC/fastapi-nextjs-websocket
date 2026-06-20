import type { Dispatch, SetStateAction } from "react";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
} from "@/types/ws";

export function handleDirectRequestMessage(
  data: DirectRequestServerMessage,
  setRequestMessages: Dispatch<SetStateAction<DirectRequestServerMessage[]>>,
): void {
  setRequestMessages((prev) => {
    if (prev.some((r) => r.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}

export function handleDirectRequestUpdated(
  data: DirectRequestUpdatedServerMessage,
  setRequestMessages: Dispatch<SetStateAction<DirectRequestServerMessage[]>>,
): void {
  setRequestMessages((prev) =>
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
