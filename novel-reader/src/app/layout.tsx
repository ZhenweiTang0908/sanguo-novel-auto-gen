import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "疯狂三国：魔改演义",
  description: "当罗贯中棺材板压不住的时候 - 世俗搞笑风格的网络小说",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%238b5cf6'/><stop offset='100%25' stop-color='%2306b6d4'/></linearGradient></defs><circle cx='50' cy='50' r='45' fill='url(%23g)'/><text x='50' y='68' font-size='50' text-anchor='middle' fill='white'>📖</text></svg>",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}