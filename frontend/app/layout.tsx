import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from '@/components/ui/toaster'
import { Navigation } from '@/components/Navigation'
import { RealTimeAlerts } from '@/components/RealTimeAlerts'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TrialEquity Platform | AI-Enhanced Clinical Trial Management',
  description: 'Premium AI-Enhanced Blockchain Platform for Secure, Fair, and Regulatory-Compliant Clinical Trial Data Management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navigation />
        <RealTimeAlerts />
        {children}
        <Toaster />
      </body>
    </html>
  )
}

