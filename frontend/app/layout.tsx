import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DevTalks — сообщество разработчиков",
  description:
    "Делись идеями, публикуй проекты и находи единомышленников в DevTalks.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
