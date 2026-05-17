import type { Dispatch, RefObject, SetStateAction } from "react";
import type {
  DirectRequestServerMessage,
  GlobalChatServerMessage,
} from "@/types/ws";

export interface HandlerDeps {
  setChatMessages: Dispatch<SetStateAction<GlobalChatServerMessage[]>>;
  setRequestMessages: Dispatch<SetStateAction<DirectRequestServerMessage[]>>;
  setError: Dispatch<SetStateAction<string | null>>;
  setSyncStatus: Dispatch<SetStateAction<string>>;
  setHeartbeatStatus: Dispatch<SetStateAction<string>>;
  lastChatId: RefObject<number | null>;
  lastRequestId: RefObject<number | null>;
  resetPingTimeout: (socket: WebSocket) => void;
  fetchMissingFeeds: () => Promise<void>;
}
