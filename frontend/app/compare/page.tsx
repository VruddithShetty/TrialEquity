'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Shield, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'

interface ComparisonData {
  hyperledger_fabric: any
  multichain: any
  quorum: any
  summary: any
}

export default function ComparePage() {
  const [data, setData] = useState<ComparisonData | null>(null)
  const [loading, setLoading] = useState(true)
  const [authenticated, setAuthenticated] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (!token || !user) {
      router.push('/login')
      return
    }
    
    try {
      // Verify token is still valid
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000
      if (exp < Date.now()) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
        return
      }
      
      setAuthenticated(true)
      fetchComparisonData()
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }, [router])

  const fetchComparisonData = async () => {
    try {
      setLoading(true)
      const result = await apiClient.compareBlockchains()
      setData(result)
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch comparison data',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  if (!authenticated) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-black py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-white mb-1">Platform Comparison</h1>
              <p className="text-white/70">Compare blockchain platforms for clinical trial management</p>
            </div>
            <BarChart3 className="h-12 w-12 text-green-400" />
          </div>

          {loading ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-gray-400">Loading comparison data...</div>
              </CardContent>
            </Card>
          ) : data ? (
            <div className="grid gap-6">
              {/* Hyperledger Fabric */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="border-green-500 bg-green-950/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                      <Shield className="h-5 w-5 text-green-400" />
                      Hyperledger Fabric
                      <span className="text-sm text-green-400 font-normal">(Recommended for Clinical Trials)</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div><strong>TPS:</strong> {data.hyperledger_fabric.tps}</div>
                      <div><strong>Latency:</strong> {data.hyperledger_fabric.latency_ms}ms</div>
                      <div><strong>Privacy:</strong> {data.hyperledger_fabric.privacy}</div>
                      <div><strong>Consensus:</strong> {data.hyperledger_fabric.consensus}</div>
                      <div><strong>Use Case:</strong> {data.hyperledger_fabric.use_case}</div>
                      <div><strong>Regulatory Suitability:</strong> {data.hyperledger_fabric.regulatory_suitability}</div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* MultiChain */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="text-white">MultiChain</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div><strong>TPS:</strong> {data.multichain.tps}</div>
                      <div><strong>Latency:</strong> {data.multichain.latency_ms}ms</div>
                      <div><strong>Privacy:</strong> {data.multichain.privacy}</div>
                      <div><strong>Consensus:</strong> {data.multichain.consensus}</div>
                      <div><strong>Use Case:</strong> {data.multichain.use_case}</div>
                      <div><strong>Regulatory Suitability:</strong> {data.multichain.regulatory_suitability}</div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Quorum */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="text-white">Quorum</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div><strong>TPS:</strong> {data.quorum.tps}</div>
                      <div><strong>Latency:</strong> {data.quorum.latency_ms}ms</div>
                      <div><strong>Privacy:</strong> {data.quorum.privacy}</div>
                      <div><strong>Consensus:</strong> {data.quorum.consensus}</div>
                      <div><strong>Use Case:</strong> {data.quorum.use_case}</div>
                      <div><strong>Regulatory Suitability:</strong> {data.quorum.regulatory_suitability}</div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Summary */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="border-yellow-500 bg-yellow-950/20">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-yellow-400" />
                      Summary & Recommendation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <p><strong>Best TPS:</strong> {data.summary.best_tps}</p>
                      <p><strong>Best Latency:</strong> {data.summary.best_latency}</p>
                      <p><strong>Best Privacy:</strong> {data.summary.best_privacy}</p>
                      <p><strong>Best Regulatory:</strong> {data.summary.best_regulatory}</p>
                      <p><strong>Easiest Deployment:</strong> {data.summary.easiest_deployment}</p>
                      <p className="mt-4 p-3 bg-yellow-500/10 rounded border border-yellow-500/20">
                        <strong>Recommendation:</strong> {data.summary.recommendation}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-gray-400">No comparison data available</div>
              </CardContent>
            </Card>
          )}

          <div className="mt-8 text-center">
            <Button onClick={fetchComparisonData} disabled={loading}>
              Refresh Comparison
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}