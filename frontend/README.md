This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## スタイリング & UIコンポーネント

本プロジェクトのスタイリングとUIコンポーネント設計には、以下のモダンな技術スタックを採用しています。

- **Panda CSS**: ビルド時に静的に解析されて CSS が出力される、Zero-runtime な CSS-in-JS です。`panda.config.ts` で定義されたデザイントークンに基づいた安全なスタイリングを実現します。本プロジェクトでは、コードの可読性と保守性を向上させるため、コンポーネントファイル (`.tsx`) からスタイル定義 (`css({...})`, `cva({...})`) を別ファイル (`*.styles.ts`) に分離して管理するアプローチを採用しています。
- **React Aria Components**: WAI-ARIAに準拠したアクセシブルかつアンスタイルのUIコンポーネントライブラリです。`Button` や `Switch` などのネイティブUIパーツの置き換えに使用され、スタイリングは Panda CSS で行っています。
- **共通UIコンポーネントのスタイル集約**: アプリケーション全体でデザインの一貫性を保つため、Input などの共通コントロールの基本デザイン（高さ、枠線、背景、フォーカス状態など）は `src/components/ui/` 配下のコンポーネントスタイルに集約しています。各機能コンポーネント（ログインフォームやチャットなど）で個別に同様のデザイン定義を行うことは避け、共通コンポーネントを利用するか、レイアウト用スタイル（`flex` や `width` など）のみを必要に応じて付与する設計ルールとしています。

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
