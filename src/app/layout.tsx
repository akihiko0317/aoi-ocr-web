import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aoi OCR - Optical Character Recognition",
  description: "Web-based OCR tool for extracting text from images",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
