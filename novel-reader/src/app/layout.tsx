import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "疯狂三国：魔改演义",
  description: "当罗贯中棺材板压不住的时候 - 世俗搞笑风格的网络小说",
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
