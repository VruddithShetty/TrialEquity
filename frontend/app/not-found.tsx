'use client'

import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Home, AlertCircle, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function NotFound() {
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
        className="max-w-md w-full relative z-10"
      >
        <Card className="blockchain-block glass-effect-premium border-red-500/30">
          <CardHeader className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="w-20 h-20 bg-gradient-to-br from-red-500/20 to-red-600/10 rounded-full flex items-center justify-center mx-auto mb-6 border-2 border-red-500/30"
            >
              <AlertCircle className="h-10 w-10 text-red-400" />
            </motion.div>
            <CardTitle className="text-4xl md:text-5xl font-bold text-white mb-2">
              404
            </CardTitle>
            <p className="text-gray-400 mt-2 text-lg">Page Not Found</p>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-center text-gray-300 leading-relaxed">
              The page you're looking for doesn't exist or has been moved.
              <br />
              <span className="text-gray-500 text-sm">Please check the URL and try again.</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Link href="/" className="flex-1">
                <Button
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300 btn-premium"
                  size="lg"
                >
                  <Home className="mr-2 h-5 w-5" />
                  Go Home
                </Button>
              </Link>
              <Button
                onClick={() => router.back()}
                variant="outline"
                className="flex-1 border-2 border-green-500/50 text-green-400 hover:bg-green-950/40 hover:border-green-400 glass-effect-premium"
                size="lg"
              >
                <ArrowLeft className="mr-2 h-5 w-5" />
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

