import type { Meta, StoryObj } from "@storybook/react";
import { fn } from "@storybook/test";
import { useRef } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";
import { GlobalChat } from "./GlobalChat";

const meta: Meta<typeof GlobalChat> = {
  title: "Features/GlobalChat/GlobalChat",
  component: GlobalChat,
  tags: ["autodocs"],
  args: {
    onTextChange: fn(),
    onSend: fn(),
    onInputKeyDown: fn(),
    onMentionSelect: fn(),
    mentionIsOpen: false,
    mentionSuggestions: [],
    mentionFocusedIndex: 0,
    formatTime: (dateStr: string) => {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    },
    typingUsers: new Set<string>(),
  },
  render: (args) => {
    const bottomRef = useRef<HTMLDivElement>(null);
    return <GlobalChat {...args} bottomRef={bottomRef} />;
  },
};

export default meta;
type Story = StoryObj<typeof GlobalChat>;

const mockMessages: GlobalChatServerMessage[] = [
  {
    type: "global_chat",
    id: 1,
    seq: 1,
    username: "alice",
    text: "Hello everyone!",
    created_at: new Date().toISOString(),
    is_history: false,
  },
  {
    type: "global_chat",
    id: 2,
    seq: 2,
    username: "bob",
    text: "Hi @alice, how are you?",
    created_at: new Date().toISOString(),
    is_history: false,
  },
  {
    type: "global_chat",
    id: 3,
    seq: 3,
    username: "alice",
    text: "I'm doing great! Just testing this WebSocket app.",
    created_at: new Date().toISOString(),
    is_history: false,
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

export const MentionDropdownOpen: Story = {
  args: {
    messages: mockMessages,
    currentUser: "alice",
    text: "@b",
    mentionIsOpen: true,
    mentionSuggestions: ["bob"],
    mentionFocusedIndex: 0,
  },
};
