'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, X } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface Alert {
  id: string
  type: 'tamper' | 'error' | 'warning'
  message: string
  timestamp: Date
  trialId?: string
}

export function RealTimeAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isOpen, setIsOpen] = useState(true)

  useEffect(() => {
    // Poll for tamper alerts (in production, this would use WebSocket)
    const interval = setInterval(async () => {
      try {
        // Check for recent tamper alerts
        // In production, this would poll /api/alerts/recent or use WebSocket
      } catch (error) {
        console.error('Error checking alerts:', error)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const addAlert = (alert: Alert) => {
    setAlerts((prev) => [alert, ...prev].slice(0, 5)) // Keep last 5 alerts
  }

  const removeAlert = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id))
  }

  // Expose addAlert for use in other components
  useEffect(() => {
    (window as any).addTamperAlert = (trialId: string) => {
      addAlert({
        id: Date.now().toString(),
        type: 'tamper',
        message: `Tampering detected in trial ${trialId}`,
        timestamp: new Date(),
        trialId,
      })
    }
  }, [])

  if (alerts.length === 0) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed top-20 right-4 z-50 max-w-md"
        >
          <Card className="border-red-200 bg-red-50 shadow-lg">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <h3 className="font-semibold text-red-900">Real-Time Alerts</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {alerts.map((alert) => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="p-3 bg-white rounded-lg border border-red-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-red-900">{alert.message}</p>
                        <p className="text-xs text-red-700 mt-1">
                          {alert.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAlert(alert.id)}
                        className="h-5 w-5 p-0 ml-2"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

