import "./globals.css";
import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Hydraulic Toolbox",
  description: "Pump and system curve analytics"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
