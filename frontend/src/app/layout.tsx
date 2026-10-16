import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { Geist } from "next/font/google";
import "@/styles/globals.css";
import { AuthProvider } from "@/features/auth/auth-provider";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", interactiveWidget: "resizes-content" };

export const metadata: Metadata = {
  title: "Study Hub | CPALE review workspace",
  description: "A focused workspace for CPALE review and study management.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={geist.variable}>
      <body><AuthProvider>{children}</AuthProvider></body>
    </html>
  );
}
