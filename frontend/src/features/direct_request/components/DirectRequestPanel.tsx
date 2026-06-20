"use client";

import { EmptyState } from "@/components/ui/composites/EmptyState/EmptyState";
import { PanelLayout } from "@/components/ui/composites/PanelLayout/PanelLayout";
import { Button, Input, Select } from "@/components/ui/primitives";
import type { UserListItem } from "@/features/auth/api";
import type { DirectRequestServerMessage, TaskStatus } from "@/types/ws";
import {
  headerSubtitleStyles,
  headerTitleStyles,
  inputGroupStyles,
  requestFormStyles,
} from "./DirectRequestPanel.styles";
import { RequestCard } from "./RequestCard/RequestCard";

export interface DirectRequestPanelProps {
  otherUsers: UserListItem[];
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
  contentRef: React.RefObject<HTMLElement | null>;
  onFetchPast: () => void;
  isFetchingPast: boolean;
  hasMorePast: boolean;
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
  contentRef,
  onFetchPast,
  isFetchingPast,
  hasMorePast,
  isSending = false,
}: DirectRequestPanelProps) {
  return (
    <PanelLayout
      contentRef={contentRef}
      header={
        <>
          <h2 className={headerTitleStyles}>ダイレクトリクエスト</h2>
          <p className={headerSubtitleStyles}>タスクの依頼や問い合わせ</p>
        </>
      }
      contentRole="region"
      contentAriaLabel="ダイレクトリクエスト一覧"
      form={
        <form onSubmit={onSend} className={requestFormStyles}>
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
                <option key={u.id} value={u.id}>
                  {u.username}
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
            disabled={!targetUser || !text.trim()}
          >
            Request
          </Button>
        </form>
      }
    >
      {hasMorePast && requests.length > 0 && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: "16px",
          }}
        >
          <Button
            type="button"
            variant="secondary"
            onClick={(e) => {
              (e.target as HTMLButtonElement).blur();
              onFetchPast();
            }}
            disabled={isFetchingPast}
          >
            {isFetchingPast ? "Loading..." : "Load older requests"}
          </Button>
        </div>
      )}
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
