import type { Meta, StoryObj } from "@storybook/react";
import { fn } from "@storybook/test";
import type { RequestMessage } from "@/types/ws";
import { RequestPanel } from "./RequestPanel";

const meta: Meta<typeof RequestPanel> = {
  title: "Features/Requests/RequestPanel",
  component: RequestPanel,
  tags: ["autodocs"],
  args: {
    onTargetUserChange: fn(),
    onTextChange: fn(),
    onSend: fn(),
    onUpdateStatus: fn(),
    formatDate: (dateStr: string) => {
      const d = new Date(dateStr);
      return d.toLocaleString("ja-JP", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
  },
};

export default meta;
type Story = StoryObj<typeof RequestPanel>;

const mockRequests: RequestMessage[] = [
  {
    type: "request",
    id: 1,
    seq: 1,
    sender: "bob",
    recipient: "alice",
    text: "資料の確認をお願いします。",
    status: "requested",
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    type: "request",
    id: 2,
    seq: 2,
    sender: "alice",
    recipient: "charlie",
    text: "バグの修正状況を教えてください。",
    status: "processing",
    created_at: new Date(Date.now() - 7200000).toISOString(),
    updated_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    type: "request",
    id: 3,
    seq: 3,
    sender: "charlie",
    recipient: "alice",
    text: "デプロイ完了しました。",
    status: "completed",
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 43200000).toISOString(),
  },
];

export const Default: Story = {
  args: {
    otherUsers: ["bob", "charlie"],
    messages: mockRequests,
    currentUser: "alice",
    targetUser: "",
    text: "",
  },
};

export const Empty: Story = {
  args: {
    otherUsers: ["bob", "charlie"],
    messages: [],
    currentUser: "alice",
    targetUser: "",
    text: "",
  },
};

export const Typing: Story = {
  args: {
    otherUsers: ["bob", "charlie"],
    messages: mockRequests,
    currentUser: "alice",
    targetUser: "bob",
    text: "急ぎでお願いします！",
  },
};
