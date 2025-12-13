import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import GlobalNav from "@/components/GlobalNav";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
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
      <body className={`${jakarta.variable} ${jetbrains.variable}`}>
        <GlobalNav />
        <div className="main-content">
          {children}
        </div>
      </body>
    </html>
  );
}
