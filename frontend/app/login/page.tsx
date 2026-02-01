'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Shield, Eye, EyeOff } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [isRedirecting, setIsRedirecting] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  // Do not auto-redirect on mount; middleware handles authenticated routing.

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    try {
      const response = await apiClient.login(email, password)
      if (response.access_token && response.user) {
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify({
          email: response.user.email,
          role: response.user.role,
          username: response.user.username
        }))
        toast({ title: 'Login successful', description: `Welcome back, ${response.user.username || email}!` })
        const dest = response.user.role === 'ADMIN' ? '/admin' : response.user.role === 'UPLOADER' ? '/upload' : '/verifier'
        router.replace(dest)
      }
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err?.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center p-4">
      <div className="fixed inset-0 blockchain-grid opacity-20 pointer-events-none" />
      <div className="fixed inset-0 hex-pattern opacity-10 pointer-events-none" />

      {isRedirecting ? (
        <div className="text-white text-xl">Redirecting...</div>
      ) : (
        <div className="w-full max-w-md space-y-6 relative z-10">
          <div className="text-center space-y-2">
            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: 'spring', stiffness: 200 }} className="flex justify-center">
              <Shield className="h-12 w-12 text-green-500" />
            </motion.div>
            <h1 className="text-3xl font-bold text-white">TrialChain</h1>
            <p className="text-gray-400">Secure Clinical Trial Management</p>
          </div>

          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Sign In</CardTitle>
              <CardDescription>Enter your credentials to access the platform</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-300">Email</Label>
                  <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="bg-gray-800 border-gray-600 text-white" placeholder="Enter your email" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-gray-300 font-medium">Password</Label>
                  <div className="relative">
                    <Input id="password" type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} required className="bg-gray-800 border-gray-600 text-white pr-12 h-12 text-base" placeholder="Enter your password" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors p-1" aria-label={showPassword ? 'Hide password' : 'Show password'}>
                      {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                    </button>
                  </div>
                </div>
                {error && (
                  <Alert className="border-red-500 bg-red-500/10">
                    <AlertDescription className="text-red-400">{error}</AlertDescription>
                  </Alert>
                )}
                <Button type="submit" disabled={isLoading} className="w-full bg-green-600 hover:bg-green-700 text-white">
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}