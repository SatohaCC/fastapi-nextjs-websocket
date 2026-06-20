import type { ReactNode } from "react";
import { Badge } from "@/components/ui/primitives";
import type { TaskStatus } from "@/types/ws";
import {
  actionGroupStyles,
  itemHeaderStyles,
  metaInfoStyles,
  requestItemStyles,
  requestPendingStyles,
  requestTextStyles,
  resolvedNoteStyles,
  senderNameStyles,
  separatorStyles,
  timestampStyles,
} from "./RequestCard.styles";

interface RequestCardProps {
  id: number;
  sender: string;
  recipient: string;
  text: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  isFromMe: boolean;
  isPending?: boolean;
  timeStr: string;
  updatedTimeStr: string;
  actionsElement?: ReactNode;
}

export function RequestCard({
  sender,
  recipient,
  text,
  status,
  isFromMe,
  isPending = false,
  timeStr,
  updatedTimeStr,
  actionsElement,
}: RequestCardProps) {
  return (
    <article
      className={`tweet-card ${requestItemStyles} ${
        isPending ? requestPendingStyles : ""
      }`}
      aria-label={isFromMe ? `${recipient} への依頼` : `${sender} からの依頼`}
    >
      <div className={itemHeaderStyles}>
        <div className={metaInfoStyles}>
          <div className={senderNameStyles}>
            {isFromMe ? `${recipient} への依頼` : `${sender} からの依頼`}
          </div>
          <div className={separatorStyles}>·</div>
          <time className={timestampStyles}>{timeStr}</time>
        </div>
        <Badge variant={status}>
          {status === "requested" && "未着手"}
          {status === "processing" && "進行中"}
          {status === "completed" && "完了"}
        </Badge>
      </div>

      <div className={requestTextStyles}>{text}</div>

      {actionsElement && (
        <div className={actionGroupStyles}>{actionsElement}</div>
      )}

      {status === "completed" && (
        <div className={resolvedNoteStyles}>
          ✓ 解決済み: <time>{updatedTimeStr}</time>
        </div>
      )}
    </article>
  );
}
