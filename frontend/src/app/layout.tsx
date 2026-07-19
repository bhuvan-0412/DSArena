import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import ClerkProviderWrapper from "@/components/shared/clerk-provider-wrapper";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DSArena | Gamified AI-Powered DSA Learning Platform",
  description: "Conquer the Striver A2Z Roadmap, earn XP, level up, unlock achievements, and master Data Structures & Algorithms in a premium RPG-style arena.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ClerkProviderWrapper>
          {children}
        </ClerkProviderWrapper>
      </body>
    </html>
  );
}
