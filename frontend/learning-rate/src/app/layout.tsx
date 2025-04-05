import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../styles/globals.css";

import Header from "@/app/components/header/header";
import Footer from "@/app/components/footer";
import { headers } from "next/headers";

const inter = Inter({ subsets: ["latin"] });


export async function generateMetadata(): Promise<Metadata> {
  const csrfToken = headers().get('X-CSRF-Token') || 'missing';

  return {
    title: "EuroRAG",
    description: "Building a fast and easy way to access Horizon Europe documents",
    other: {
      'x-csrf-token': csrfToken,
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
