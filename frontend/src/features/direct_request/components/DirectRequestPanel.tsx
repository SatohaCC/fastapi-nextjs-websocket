"use client";

import { Badge } from "@/components/ui/Badge/Badge";
import { Button } from "@/components/ui/Button/Button";
import { Input, Select } from "@/components/ui/Input/Input";
import { PanelLayout } from "@/components/ui/PanelLayout/PanelLayout";
import type { DirectRequestServerMessage, TaskStatus } from "@/types/ws";
import {
  actionButtonStyles,
  actionGroupStyles,
  completeButtonStyles,
  emptyStateStyles,
  formGridStyles,
  inputGroupStyles,
  inputTaskStyles,
  itemHeaderStyles,
  metaInfoStyles,
  requestFormStyles,
  requestItemStyles,
  requestListStyles,
  requestPendingStyles,
  requestTextStyles,
  resolvedNoteStyles,
  selectRecipientStyles,
  senderNameStyles,
  separatorStyles,
  submitButtonStyles,
  subtitleStyles,
  timestampStyles,
  titleStyles,
} from "./DirectRequestPanel.styles";

export interface DirectRequestPanelProps {
  otherUsers: string[];
  requests: (DirectRequestServerMessage & { isPending?: boolean })[];
  currentUser: string;
  targetUser: string;
  text: string;
  onTargetUserChange: (value: string) => void;
  onTextChange: (value: string) => void;
  onSend: (e: React.FormEvent) => void;
  onUpdateStatus: (id: number, status: TaskStatus) => void;
  formatDate: (dateStr: string) => string;
  bottomRef: React.RefObject<HTMLDivElement | null>;
  isSending?: boolean;
}

export function DirectRequestPanel({
  otherUsers,
  requests,
  currentUser,
  targetUser,
  text,
  onTargetUserChange,
  onTextChange,
  onSend,
  onUpdateStatus,
  formatDate,
  bottomRef,
  isSending = false,
}: DirectRequestPanelProps) {
  return (
    <PanelLayout
      header={
        <>
          <h2 className={titleStyles}>ダイレクトリクエスト</h2>
          <p className={subtitleStyles}>タスクの依頼や問い合わせ</p>
        </>
      }
      contentClassName={requestListStyles}
      contentRole="region"
      contentAriaLabel="ダイレクトリクエスト一覧"
      form={
        <form onSubmit={onSend} className={requestFormStyles}>
          <div className={formGridStyles}>
            <div className={inputGroupStyles}>
              <label htmlFor="direct-request-recipient" className="sr-only">
                依頼先を選択
              </label>
              <Select
                id="direct-request-recipient"
                value={targetUser}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  onTargetUserChange(e.target.value)
                }
                className={selectRecipientStyles}
                disabled={isSending}
              >
                <option value="" disabled>
                  依頼先を選択
                </option>
                {otherUsers.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </Select>
              <label htmlFor="direct-request-text" className="sr-only">
                依頼内容を入力
              </label>
              <Input
                id="direct-request-text"
                type="text"
                value={text}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onTextChange(e.target.value)
                }
                placeholder="依頼内容を入力してください"
                className={inputTaskStyles}
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              className={submitButtonStyles}
              disabled={!targetUser || !text.trim()}
            >
              リクエストを送信
            </Button>
          </div>
        </form>
      }
    >
      {requests.length === 0 ? (
        <div className={emptyStateStyles}>現在リクエストはありません。</div>
      ) : (
        requests.map((m) => {
          const isFromMe = m.sender === currentUser;
          const canUpdate =
            m.recipient === currentUser && m.status !== "completed";

          return (
            <article
              key={m.id}
              className={`tweet-card ${requestItemStyles} ${
                m.isPending ? requestPendingStyles : ""
              }`}
              aria-label={
                isFromMe ? `${m.recipient} への依頼` : `${m.sender} からの依頼`
              }
            >
              <div className={itemHeaderStyles}>
                <div className={metaInfoStyles}>
                  <div className={senderNameStyles}>
                    {isFromMe
                      ? `${m.recipient} への依頼`
                      : `${m.sender} からの依頼`}
                  </div>
                  <div className={separatorStyles}>·</div>
                  <time dateTime={m.created_at} className={timestampStyles}>
                    {formatDate(m.created_at)}
                  </time>
                </div>
                <Badge variant={m.status}>
                  {m.status === "requested" && "未着手"}
                  {m.status === "processing" && "進行中"}
                  {m.status === "completed" && "完了"}
                </Badge>
              </div>

              <div className={requestTextStyles}>{m.text}</div>

              {canUpdate && (
                <div className={actionGroupStyles}>
                  {m.status === "requested" && (
                    <Button
                      type="button"
                      onClick={() => onUpdateStatus(m.id, "processing")}
                      variant="secondary"
                      className={actionButtonStyles}
                      aria-label={`${m.sender} からの依頼「${m.text}」を承諾する`}
                    >
                      承諾
                    </Button>
                  )}
                  <Button
                    type="button"
                    onClick={() => onUpdateStatus(m.id, "completed")}
                    variant="primary"
                    className={`${actionButtonStyles} ${completeButtonStyles}`}
                    aria-label={`${m.sender} からの依頼「${m.text}」を完了する`}
                  >
                    完了
                  </Button>
                </div>
              )}

              {m.status === "completed" && (
                <div className={resolvedNoteStyles}>
                  ✓ 解決済み:{" "}
                  <time dateTime={m.updated_at}>
                    {formatDate(m.updated_at)}
                  </time>
                </div>
              )}
            </article>
          );
        })
      )}
      <div ref={bottomRef} />
    </PanelLayout>
  );
}
