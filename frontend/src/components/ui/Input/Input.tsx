import type { SelectHTMLAttributes } from "react";
import {
  Input as RACInput,
  type InputProps as RACInputProps,
} from "react-aria-components";
import { inputStyles, selectStyles } from "./Input.styles";

/**
 * 共通デザインが適用されたインプットコンポーネント。
 * アプリケーション内のすべてのテキスト入力フィールドはこのコンポーネントに統一され、
 * 各機能側で個別にデザインスタイルを定義せず、本コンポーネントの共通スタイルを使用します。
 */
export function Input({ className = "", ...props }: RACInputProps) {
  return (
    <RACInput className={`${inputStyles} ${className}`.trim()} {...props} />
  );
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
}

/**
 * 共通デザインが適用されたセレクトコンポーネント。
 * 入力コンポーネントと高さを揃え、アプリケーション全体で統一感のあるセレクトボックスを提供します。
 */
export function Select({ className = "", children, ...props }: SelectProps) {
  return (
    <select className={`${selectStyles} ${className}`.trim()} {...props}>
      {children}
    </select>
  );
}
