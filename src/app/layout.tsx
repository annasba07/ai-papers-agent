import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import GlobalNav from "@/components/GlobalNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Paper Atlas | Research Intelligence Platform",
  description: "Discover breakthrough AI research, track trends, and generate working code from papers using multi-agent systems.",
  keywords: ["AI research", "machine learning", "papers", "code generation", "trends"],
  openGraph: {
    title: "AI Paper Atlas",
    description: "Track AI research trends and generate code from papers",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <GlobalNav />
        <div className="main-content">
          {children}
        </div>
      </body>
    </html>
  );
}
