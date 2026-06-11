import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./Badge";

const meta: Meta<typeof Badge> = {
  title: "UI/Badge",
  component: Badge,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: [
        "requested",
        "processing",
        "completed",
        "error",
        "warning",
        "default",
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Badge>;

export const Default: Story = {
  args: {
    variant: "default",
    children: "Default",
  },
};

export const Requested: Story = {
  args: {
    variant: "requested",
    children: "Requested",
  },
};

export const Processing: Story = {
  args: {
    variant: "processing",
    children: "Processing",
  },
};

export const Completed: Story = {
  args: {
    variant: "completed",
    children: "Completed",
  },
};

export const ErrorState: Story = {
  args: {
    variant: "error",
    children: "Error",
  },
};

export const Warning: Story = {
  args: {
    variant: "warning",
    children: "Warning",
  },
};
