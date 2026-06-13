import type { Meta, StoryObj } from "@storybook/react";
import { expect, within } from "@storybook/test";
import { OnlineUsers } from "./OnlineUsers";

const meta: Meta<typeof OnlineUsers> = {
  title: "Features/Presence/OnlineUsers",
  component: OnlineUsers,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof OnlineUsers>;

export const Default: Story = {
  args: {
    usernames: ["alice", "bob", "charlie"],
    currentUsername: "alice",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    expect(canvas.getByText("オンライン (3)")).toBeInTheDocument();
    // 自分のチップには「（あなた）」が付く。
    expect(canvas.getByLabelText("alice（あなた）")).toBeInTheDocument();
  },
};

export const Empty: Story = {
  args: {
    usernames: [],
    currentUsername: "alice",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    expect(canvas.getByText("オンライン (0)")).toBeInTheDocument();
    expect(
      canvas.getByText("誰もオンラインではありません"),
    ).toBeInTheDocument();
  },
};

export const Loading: Story = {
  args: {
    usernames: [],
    currentUsername: "alice",
    isReady: false,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // 未受信時は「0人/誰もいない」を出さずローディング表示にする。
    expect(canvas.getByText("オンライン状況を取得中…")).toBeInTheDocument();
    expect(canvas.queryByText("オンライン (0)")).not.toBeInTheDocument();
  },
};
