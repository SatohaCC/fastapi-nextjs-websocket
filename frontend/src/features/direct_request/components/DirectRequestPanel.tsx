"use client";

import { EmptyState } from "@/components/ui/composites/EmptyState/EmptyState";
import { PanelLayout } from "@/components/ui/composites/PanelLayout/PanelLayout";
import { Button } from "@/components/ui/primitives/Button/Button";
import { Input, Select } from "@/components/ui/primitives/Input/Input";
import { css } from "@/styled-system/css";
import type { DirectRequestServerMessage, TaskStatus } from "@/types/ws";
import { RequestCard } from "./RequestCard/RequestCard";

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

const requestFormStyles = css({
  padding: "12px 16px",
  background: "panelBg",
});

const formGridStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "10px",
});

const inputGroupStyles = css({
  display: "flex",
  gap: "8px",
  overflow: "hidden",
  minWidth: "0",
  "& select": {
    flex: "0 0 auto",
    width: "160px!",
  },
  "& input": {
    flex: "1",
    minWidth: "0",
    width: "auto!",
  },
});

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
          <h2
            className={css({
              fontSize: "15px",
              fontWeight: 500,
              color: "textPrimary",
              letterSpacing: "0.01em",
            })}
          >
            ダイレクトリクエスト
          </h2>
          <p
            className={css({
              fontSize: "12px",
              color: "textSecondary",
              marginTop: "2px",
            })}
          >
            タスクの依頼や問い合わせ
          </p>
        </>
      }
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
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              fullWidth
              disabled={!targetUser || !text.trim()}
            >
              リクエストを送信
            </Button>
          </div>
        </form>
      }
    >
      {requests.length === 0 ? (
        <EmptyState message="現在リクエストはありません。" />
      ) : (
        requests.map((m) => {
          const isFromMe = m.sender === currentUser;
          const canUpdate =
            m.recipient === currentUser && m.status !== "completed";

          return (
            <RequestCard
              key={m.id}
              id={m.id}
              sender={m.sender}
              recipient={m.recipient}
              text={m.text}
              status={m.status}
              created_at={m.created_at}
              updated_at={m.updated_at}
              isFromMe={isFromMe}
              isPending={m.isPending}
              timeStr={formatDate(m.created_at)}
              updatedTimeStr={formatDate(m.updated_at)}
              actionsElement={
                canUpdate ? (
                  <>
                    {m.status === "requested" && (
                      <Button
                        type="button"
                        onClick={() => onUpdateStatus(m.id, "processing")}
                        variant="secondary"
                        size="sm"
                        aria-label={`${m.sender} からの依頼「${m.text}」を承諾する`}
                      >
                        承諾
                      </Button>
                    )}
                    <Button
                      type="button"
                      onClick={() => onUpdateStatus(m.id, "completed")}
                      variant="success"
                      size="sm"
                      aria-label={`${m.sender} からの依頼「${m.text}」を完了する`}
                    >
                      完了
                    </Button>
                  </>
                ) : undefined
              }
            />
          );
        })
      )}
      <div ref={bottomRef} />
    </PanelLayout>
  );
}
