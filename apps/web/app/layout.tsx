import type { Metadata } from "next";
import "./globals.css";
import "./news/news.css";
import "./travel/travel.css";

export const metadata: Metadata = { title: "PathWell", description: "One life. Many goals. One clear path." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
