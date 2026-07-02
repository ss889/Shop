import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Shopping Agent",
  description: "Multi-agent product search with decision logging",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
