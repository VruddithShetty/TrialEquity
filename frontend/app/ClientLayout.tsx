'use client'

import { usePathname } from 'next/navigation'
import { Navigation } from '@/components/Navigation'
import { RealTimeAlerts } from '@/components/RealTimeAlerts'

interface ClientLayoutProps {
  children: React.ReactNode
}

export function ClientLayout({ children }: ClientLayoutProps) {
  const pathname = usePathname()
  
  // Don't show navigation on login page
  const showNavigation = pathname !== '/login'
  
  return (
    <>
      {showNavigation && <Navigation />}
      {children}
      {showNavigation && <RealTimeAlerts />}
    </>
  )
}
