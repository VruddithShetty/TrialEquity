'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Upload, Brain, Link2, Shield, BarChart3, Settings, Activity, CheckCircle } from 'lucide-react'
import { FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function Navigation() {
  const pathname = usePathname()

  // Get user role from localStorage
  const getUserRole = () => {
    try {
      const user = localStorage.getItem('user')
      if (user) {
        const userData = JSON.parse(user)
        return userData.role
      }
    } catch (e) {
      // Ignore
    }
    return null
  }

  const userRole = getUserRole()

  const navItems = [
    { href: '/upload', label: 'Upload', icon: Upload, roles: ['ADMIN', 'UPLOADER'] },
    { href: '/files', label: 'Files', icon: FileText, roles: ['ADMIN', 'UPLOADER', 'VALIDATOR'] },
    { href: '/verifier', label: 'Verifier', icon: CheckCircle, roles: ['ADMIN', 'VALIDATOR'] },
    { href: '/ml-analysis', label: 'ML Analysis', icon: Brain, roles: ['ADMIN'] },
    { href: '/blockchain', label: 'Blockchain', icon: Link2, roles: ['ADMIN'] },
    { href: '/compare', label: 'Compare', icon: BarChart3, roles: ['ADMIN'] },
    // Regulator and Admin removed from main nav for ADMIN users - accessible via direct URL
  ].filter(item => !userRole || item.roles.includes(userRole))

  return (
    <nav className="border-b border-green-900/40 bg-black/98 backdrop-blur-xl sticky top-0 z-50 shadow-2xl shadow-green-500/20">
      <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 via-transparent to-green-500/5" />
      <div className="container mx-auto px-4 relative">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-green-500 rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
              <div className="relative bg-gradient-to-br from-green-600 to-green-500 p-2 rounded-lg">
                <Activity className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-xl text-white leading-tight">TrialEquity</span>
              <span className="text-xs text-green-400 leading-tight font-medium">Enterprise Platform</span>
            </div>
          </Link>
          
          <div className="flex items-center gap-4">
            {userRole && (
              <div className="flex items-center gap-2 px-4 py-2 glass rounded-lg border border-green-500/40">
                <span className="text-xs text-green-300 font-medium">Role:</span>
                <span className="text-sm font-bold text-green-400">{userRole}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || 
                (item.href !== '/' && pathname?.startsWith(item.href))
              
              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={isActive ? 'default' : 'ghost'}
                    className={cn(
                      'flex items-center gap-2 transition-all duration-300 relative group',
                      isActive 
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg shadow-green-500/50 hover:from-green-500 hover:to-emerald-500' 
                        : 'text-gray-300 hover:text-white hover:bg-white/10 hover:shadow-md hover:shadow-green-500/20'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Button>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

