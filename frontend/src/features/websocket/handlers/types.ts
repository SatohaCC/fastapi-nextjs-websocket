import type { Dispatch, RefObject, SetStateAction } from "react";
import type { ChatMessage, RequestMessage } from "@/types/ws";

/** 各ハンドラが共有する依存オブジェクト */
export interface HandlerDeps {
  setChatMessages: Dispatch<SetStateAction<ChatMessage[]>>;
  setRequestMessages: Dispatch<SetStateAction<RequestMessage[]>>;
  setError: Dispatch<SetStateAction<string | null>>;
  setSyncStatus: Dispatch<SetStateAction<string>>;
  setHeartbeatStatus: Dispatch<SetStateAction<string>>;
  lastChatId: RefObject<number | null>;
  lastRequestId: RefObject<number | null>;
  resetPingTimeout: (socket: WebSocket) => void;
  fetchMissingFeeds: () => Promise<void>;
}
