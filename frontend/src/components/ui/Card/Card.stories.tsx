import type { Meta, StoryObj } from "@storybook/react";
import { Card, CardContent, CardHeader } from "./Card";

const meta: Meta<typeof Card> = {
  title: "UI/Card",
  component: Card,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    children: (
      <>
        <CardHeader>Card Header</CardHeader>
        <CardContent>
          <p>This is the content of the card.</p>
        </CardContent>
      </>
    ),
  },
};

export const Hoverable: Story = {
  args: {
    hoverable: true,
    children: (
      <>
        <CardHeader>Hoverable Card</CardHeader>
        <CardContent>
          <p>Hover over this card to see the effect.</p>
        </CardContent>
      </>
    ),
  },
};

export const Simple: Story = {
  args: {
    children: <CardContent>Simple card without header.</CardContent>,
  },
};
