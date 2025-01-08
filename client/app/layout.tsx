import { Inter } from "next/font/google";
import { Metadata } from 'next/types';
import { ReactNode } from 'react';
import ClientProvider from '../components/ClientProvider';
import './globals.css';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Thavalon - A Social Deduction Game",
  description: "A social deduction game based on The Resistance and Avalon for 5 to 10 players. Play with friends online or in person!",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientProvider>
          {children}
        </ClientProvider>
      </body>
    </html>
  );
}
