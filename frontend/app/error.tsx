'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
  }, [error])

  const router = useRouter()

  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="fixed inset-0 blockchain-grid opacity-30" />
      <div className="fixed inset-0 hex-pattern opacity-20" />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="max-w-lg w-full relative z-10"
      >
        <Card className="blockchain-block glass-effect-premium border-red-500/40">
          <CardHeader className="text-center">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="w-20 h-20 bg-gradient-to-br from-red-500/20 to-red-600/10 rounded-full flex items-center justify-center mx-auto mb-6 border-2 border-red-500/40"
            >
              <AlertTriangle className="h-10 w-10 text-red-400" />
            </motion.div>
            <CardTitle className="text-3xl md:text-4xl font-bold text-white mb-2">
              Something went wrong!
            </CardTitle>
            <p className="text-gray-400 mt-2 text-base">
              {error.message || 'An unexpected error occurred'}
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-center text-gray-300 leading-relaxed">
              We're sorry, but something unexpected happened.
              <br />
              <span className="text-gray-500 text-sm">Please try again or return to the home page.</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={reset}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300 btn-premium"
                size="lg"
              >
                <RefreshCw className="mr-2 h-5 w-5" />
                Try Again
              </Button>
              <Link href="/" className="flex-1">
                <Button
                  variant="outline"
                  className="w-full border-2 border-green-500/50 text-green-400 hover:bg-green-950/40 hover:border-green-400 glass-effect-premium"
                  size="lg"
                >
                  <Home className="mr-2 h-5 w-5" />
                  Go Home
                </Button>
              </Link>
            </div>
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-4 glass-effect rounded-lg p-4 border border-gray-700">
                <summary className="cursor-pointer text-sm text-gray-400 hover:text-gray-300 transition-colors">
                  Error Details (Development Only)
                </summary>
                <pre className="mt-3 p-4 bg-black/50 rounded text-xs overflow-auto max-h-48 text-red-300 font-mono border border-gray-800">
                  {error.stack || error.message}
                </pre>
              </details>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

