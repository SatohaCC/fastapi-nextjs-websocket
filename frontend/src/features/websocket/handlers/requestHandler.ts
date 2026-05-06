import { mergeById } from "@/features/websocket/utils/mergeById";
import type { RequestMessage, RequestUpdateMessage } from "@/types/ws";
import type { HandlerDeps } from "./types";

/** リクエストメッセージを受信し、状態を更新する */
export function handleRequestMessage(
  data: RequestMessage,
  deps: HandlerDeps,
): void {
  deps.setRequestMessages((prev) => {
    if (prev.some((r) => r.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}

/** リクエストのステータス更新を処理する */
export function handleRequestUpdated(
  data: RequestUpdateMessage,
  deps: HandlerDeps,
): void {
  deps.setRequestMessages((prev) =>
    prev.map((r) =>
      r.id === data.id
        ? {
            ...r,
            status: data.status,
            updated_at: data.updated_at,
          }
        : r,
    ),
  );
}
