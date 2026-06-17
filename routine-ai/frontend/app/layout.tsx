import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import PushInit from "@/components/PushInit";

const geist = Geist({ variable: "--font-geist", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "루틴 AI",
  description: "AI 개인 비서 — 루틴 알리미",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className={`${geist.variable} h-full`}>
      <body className="min-h-full bg-gray-950 text-gray-100 antialiased">
        <PushInit />
        <nav className="flex items-center gap-6 px-6 py-4 border-b border-gray-800">
          <span className="font-bold text-white text-lg">루틴 AI</span>
          <Link href="/" className="text-sm text-gray-400 hover:text-white transition-colors">
            오늘
          </Link>
          <Link href="/chat" className="text-sm text-gray-400 hover:text-white transition-colors">
            AI 채팅
          </Link>
          <Link href="/routines" className="text-sm text-gray-400 hover:text-white transition-colors">
            루틴 관리
          </Link>
        </nav>
        <main className="max-w-2xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
