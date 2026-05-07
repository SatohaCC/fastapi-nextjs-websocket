import type { Meta, StoryObj } from "@storybook/react";
import { fn } from "@storybook/test";
import type { ChatMessage } from "@/types/ws";
import { GlobalChat } from "./GlobalChat";

const meta: Meta<typeof GlobalChat> = {
  title: "Features/Chat/GlobalChat",
  component: GlobalChat,
  tags: ["autodocs"],
  args: {
    onTextChange: fn(),
    onSend: fn(),
    formatTime: (dateStr: string) => {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    },
  },
};

export default meta;
type Story = StoryObj<typeof GlobalChat>;

const mockMessages: ChatMessage[] = [
  {
    type: "message",
    id: 1,
    seq: 1,
    username: "alice",
    text: "Hello everyone!",
    created_at: new Date().toISOString(),
  },
  {
    type: "message",
    id: 2,
    seq: 2,
    username: "bob",
    text: "Hi Alice, how are you?",
    created_at: new Date().toISOString(),
  },
  {
    type: "message",
    id: 3,
    seq: 3,
    username: "alice",
    text: "I'm doing great! Just testing this WebSocket app.",
    created_at: new Date().toISOString(),
  },
];

export const Default: Story = {
  args: {
    messages: mockMessages,
    currentUser: "alice",
    text: "",
  },
};

export const Empty: Story = {
  args: {
    messages: [],
    currentUser: "alice",
    text: "",
  },
};

export const WithText: Story = {
  args: {
    messages: mockMessages,
    currentUser: "alice",
    text: "Typing a new message...",
  },
};
