import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Modern WS Chat",
  description: "Next.js 16 + FastAPI WebSocket Chat App",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
