"use client";

import { Badge } from "@/components/ui/Badge/Badge";
import { Button } from "@/components/ui/Button/Button";
import { Input, Select } from "@/components/ui/Input/Input";
import { PanelLayout } from "@/components/ui/PanelLayout/PanelLayout";
import { css } from "@/styled-system/css";
import type { DirectRequestServerMessage, TaskStatus } from "@/types/ws";

const titleStyles = css({
  fontSize: "17px",
  fontWeight: 800,
});

const subtitleStyles = css({
  fontSize: "12px",
  color: "textSecondary",
});

const requestFormStyles = css({
  padding: "16px 20px",
});

const formGridStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "10px",
});

const inputGroupStyles = css({
  display: "flex",
  gap: "10px",
});

const selectRecipientStyles = css({
  flex: 1,
  borderRadius: "20px",
  backgroundColor: "#16181c",
});

const inputTaskStyles = css({
  flex: 2,
  borderRadius: "20px",
  background: "#16181c",
  border: "1px solid transparent",
});

const submitButtonStyles = css({
  fontSize: "15px",
  padding: "10px 0",
});

const requestListStyles = css({
  display: "flex",
  flexDirection: "column",
});

const emptyStateStyles = css({
  textAlign: "center",
  color: "textSecondary",
  padding: "40px 20px",
  fontSize: "14px",
});

const requestItemStyles = css({
  padding: "16px 20px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
});

const itemHeaderStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  marginBottom: "8px",
});

const metaInfoStyles = css({
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

const senderNameStyles = css({
  fontSize: "13px",
  fontWeight: 800,
});

const separatorStyles = css({
  color: "textSecondary",
});

const timestampStyles = css({
  fontSize: "11px",
  color: "textSecondary",
});

const requestTextStyles = css({
  fontSize: "14px",
  lineHeight: 1.5,
  marginBottom: "12px",
  color: "#e7e9ea",
  wordBreak: "break-word",
});

const actionGroupStyles = css({
  display: "flex",
  gap: "8px",
  marginTop: "12px",
});

const actionButtonStyles = css({
  fontSize: "14px",
  padding: "8px 0",
  flex: 1,
});

const completeButtonStyles = css({
  background: "status.completed!",
});

const resolvedNoteStyles = css({
  fontSize: "11px",
  color: "status.completed",
  fontWeight: 600,
  marginTop: "8px",
});

const requestPendingStyles = css({
  opacity: 0.5,
});

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
