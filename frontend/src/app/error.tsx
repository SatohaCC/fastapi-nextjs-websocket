"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button/Button";
import {
  containerStyles,
  detailBoxStyles,
  headingStyles,
  messageStyles,
} from "./error.styles";

export default function ChatError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // biome-ignore lint/suspicious/noConsole: Error logging is necessary in the error boundary
    console.error(error);
  }, [error]);

  return (
    <div className={containerStyles}>
      <div className={headingStyles}>システムエラー</div>
      <p className={messageStyles}>
        システムとの同期中に予期しないエラーが発生しました。
        サーバーとの接続が切断されています。
      </p>
      <div className={detailBoxStyles}>
        {error.message || "原因不明のエラーが検出されました"}
      </div>
      <Button onPress={() => reset()}>再接続を試みる</Button>
    </div>
  );
}
