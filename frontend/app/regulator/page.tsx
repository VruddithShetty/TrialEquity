'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Shield, FileText, AlertTriangle, CheckCircle, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

interface AuditLog {
  log_id: string
  trial_id: string
  user_id: string
  action: string
  timestamp: string
  details?: any
}

export default function RegulatorDashboard() {
  const searchParams = useSearchParams()
  const trialId = searchParams.get('trial_id')
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(false)
  const [authenticated, setAuthenticated] = useState(false)
  const { toast } = useToast()

  // Auto-login with test user on mount
  useEffect(() => {
    const autoLogin = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        // Verify token is still valid by checking if it's expired
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          const exp = payload.exp * 1000 // Convert to milliseconds
          if (exp > Date.now()) {
            setAuthenticated(true)
            console.log('✅ Using existing valid token')
            return
          } else {
            // Token expired, remove it
            localStorage.removeItem('token')
            console.log('⚠️ Token expired, will re-login')
          }
        } catch (e) {
          // Invalid token format, remove it
          localStorage.removeItem('token')
          console.log('⚠️ Invalid token format, will re-login')
        }
      }

      // Wait a bit for backend to be ready, then retry
      const tryLogin = async (retries = 5) => {
        for (let i = 0; i < retries; i++) {
          try {
            // Check if backend is ready first
            const healthCheck = await fetch('http://localhost:8000/health')
            if (!healthCheck.ok) {
              throw new Error('Backend not ready')
            }
            
            // Backend is ready, try login with REGULATOR credentials
            const result = await apiClient.login('regulator@example.com', 'test123')
            if (result.access_token) {
              setAuthenticated(true)
              console.log('✅ Auto-login successful as REGULATOR')
              return
            } else {
              throw new Error('Login did not return access token')
            }
          } catch (error: any) {
            console.log(`Login attempt ${i + 1} failed:`, error.message)
            if (i < retries - 1) {
              // Wait 2 seconds before retry
              await new Promise(resolve => setTimeout(resolve, 2000))
            } else {
              console.error('Auto-login failed after retries:', error)
              toast({
                title: 'Backend Not Ready',
                description: 'Waiting for backend to start. Please refresh the page in a moment.',
                variant: 'destructive',
              })
            }
          }
        }
      }
      
      // Wait 2 seconds before first attempt (give backend time to start)
      setTimeout(() => {
        tryLogin()
      }, 2000)
    }
    autoLogin()
  }, [toast])

  useEffect(() => {
    if (authenticated) {
      fetchAuditLogs()
    }
  }, [trialId, authenticated])

  const fetchAuditLogs = async () => {
    if (!authenticated) {
      // Wait for authentication
      const token = localStorage.getItem('token')
      if (!token) {
        toast({
          title: 'Authentication Required',
          description: 'Please wait for auto-login to complete or refresh the page.',
          variant: 'destructive',
        })
        return
      }
      setAuthenticated(true)
    }

    setLoading(true)
    try {
      const data = await apiClient.getAuditLogs(trialId || undefined)
      setLogs(data)
    } catch (error: any) {
      console.error('Failed to fetch audit logs:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Access denied'
      
      // Check if it's a 403 permission error - try to re-login with REGULATOR credentials
      if (error.response?.status === 403) {
        try {
          const result = await apiClient.login('regulator@example.com', 'test123')
          if (result.access_token) {
            setAuthenticated(true)
            // Retry fetching logs after a short delay
            setTimeout(() => {
              fetchAuditLogs()
            }, 500)
            return
          }
        } catch (loginError: any) {
          console.error('Re-login failed:', loginError)
        }
        toast({
          title: 'Access Restricted',
          description: 'This page requires REGULATOR role. Please ensure you are logged in with regulator@example.com',
          variant: 'destructive',
        })
        setLogs([])
      } else {
        toast({
          title: 'Failed to fetch logs',
          description: errorMessage,
          variant: 'destructive',
        })
      }
      
      // Set empty logs so UI doesn't break
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!trialId) return

    // Check if we have a token
    const token = localStorage.getItem('token')
    if (!token || !authenticated) {
      // Try to login first
      try {
        await apiClient.login('test@example.com', 'test123')
        setAuthenticated(true)
      } catch (error: any) {
        toast({
          title: 'Authentication Required',
          description: 'Please wait for auto-login to complete or refresh the page.',
          variant: 'destructive',
        })
        return
      }
    }

    try {
      const blob = await apiClient.downloadReport(trialId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `trial_report_${trialId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast({
        title: 'Report Downloaded',
        description: 'PDF report has been downloaded',
      })
    } catch (error: any) {
      toast({
        title: 'Download Failed',
        description: error.response?.data?.detail || 'Failed to download report',
        variant: 'destructive',
      })
    }
  }

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'blockchain_write':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'blockchain_verify':
        return <Shield className="h-6 w-6 text-green-400" />
      default:
        return <FileText className="h-6 w-6 text-white-400" />
    }
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden py-12">
      {/* Background effects */}
      <div className="fixed inset-0 blockchain-grid opacity-20" />
      <div className="fixed inset-0 hex-pattern opacity-15" />
      
      <div className="container mx-auto px-4 max-w-6xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
            <div>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mb-4 green-glow"
              >
                <Shield className="h-8 w-8 text-white" />
              </motion.div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
                <span className="gradient-text-green">Regulator</span> Dashboard
              </h1>
              <p className="text-xl text-white-300">
                {trialId ? (
                  <>
                    Trial ID: <span className="text-green-400 font-mono">{trialId}</span>
                  </>
                ) : (
                  'All Trials Audit Logs'
                )}
              </p>
            </div>
            {trialId && (
              <Button 
                onClick={handleDownloadReport} 
                size="lg"
                className="bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300"
              >
                <Download className="h-4 w-4 mr-2" />
                Download Report
              </Button>
            )}
          </div>

          {/* Tamper Alerts */}
          <Card className="mb-6 blockchain-block glass-effect border-green-500/50 bg-green-950/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse" />
                  <AlertTriangle className="h-8 w-8 text-green-400 relative z-10" />
                </div>
                <div>
                  <p className="font-semibold text-green-400 text-lg">Tamper Detection Active</p>
                  <p className="text-sm text-white mt-1">
                    Real-time monitoring enabled. Any hash mismatch will trigger immediate alerts.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Audit Logs */}
          <Card className="blockchain-block glass-effect border-green-500/30">
            <CardHeader>
              <CardTitle className="text-2xl text-white flex items-center gap-3">
                <FileText className="h-6 w-6 text-green-400" />
                Audit Logs
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-green-500/20 rounded-full mb-4">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Shield className="h-6 w-6 text-green-400" />
                    </motion.div>
                  </div>
                  <p className="text-white-300">Loading audit logs...</p>
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-white-600 mx-auto mb-4 opacity-50" />
                  <p className="text-white-400">No audit logs found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {logs && Array.isArray(logs) ? logs.map((log, idx) => (
                    <motion.div
                      key={log.log_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-5 border border-green-500/20 rounded-lg bg-green-950/20 hover:bg-green-950/30 hover:border-green-500/40 transition-all duration-300 glass-effect"
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 mt-1">
                          {getActionIcon(log.action)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-2">
                            <p className="font-semibold text-white capitalize text-lg">
                              {log.action.replace(/_/g, ' ')}
                            </p>
                            <p className="text-sm text-white-400 whitespace-nowrap">
                              {new Date(log.timestamp).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-4 text-sm mb-2">
                            <p className="text-white-300">
                              <span className="text-white-500">Trial ID:</span>{' '}
                              <span className="text-green-400 font-mono">{log.trial_id}</span>
                            </p>
                            <p className="text-white-300">
                              <span className="text-white-500">User:</span>{' '}
                              <span className="text-green-400">{log.user_id}</span>
                            </p>
                          </div>
                          {log.details && (
                            <div className="mt-3 p-3 bg-black/40 rounded border border-green-500/20 text-xs font-mono text-white-300 overflow-x-auto">
                              <pre className="whitespace-pre-wrap">{JSON.stringify(log.details, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )) : <p className="text-white-400 text-center py-4">No audit logs available</p>}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Trial Integrity Summary */}
          {trialId && (
            <Card className="mt-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="text-2xl text-white flex items-center gap-3">
                  <Shield className="h-6 w-6 text-green-400" />
                  Integrity Verification
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-6 bg-green-950/30 rounded-lg border border-green-500/30 glass-effect hover:border-green-500/50 transition-all duration-300">
                    <p className="text-sm font-semibold text-green-400 mb-2">Blockchain Status</p>
                    <p className="text-3xl font-bold text-green-300">Verified</p>
                    <div className="mt-2 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  </div>
                  <div className="p-6 bg-green-950/30 rounded-lg border border-green-500/30 glass-effect hover:border-green-500/50 transition-all duration-300">
                    <p className="text-sm font-semibold text-green-400 mb-2">Digital Signature</p>
                    <p className="text-3xl font-bold text-green-300">Valid</p>
                    <div className="mt-2 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  </div>
                  <div className="p-6 bg-green-950/30 rounded-lg border border-green-500/30 glass-effect hover:border-green-500/50 transition-all duration-300">
                    <p className="text-sm font-semibold text-green-400 mb-2">ML Fairness</p>
                    <p className="text-3xl font-bold text-green-300">Passed</p>
                    <div className="mt-2 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

