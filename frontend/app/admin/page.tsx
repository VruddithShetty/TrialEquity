'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings, Users, Server, Brain, RefreshCw, Shield } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'

export default function AdminPage() {
  const [loading, setLoading] = useState(false)
  const [retraining, setRetraining] = useState(false)
  const [nodes, setNodes] = useState<any[]>([])
  const [users, setUsers] = useState<any[]>([])
  const { toast } = useToast()

  useEffect(() => {
    fetchNodes()
    fetchUsers()
  }, [])

  const fetchNodes = async () => {
    try {
      const data = await apiClient.getNodes()
      setNodes(data.nodes || [])
    } catch (error: any) {
      console.error('Failed to fetch nodes:', error)
    }
  }

  const fetchUsers = async () => {
    try {
      const data = await apiClient.getUsers()
      setUsers(data.users || [])
    } catch (error: any) {
      console.error('Failed to fetch users:', error)
    }
  }

  const handleRetrainModel = async () => {
    setRetraining(true)
    try {
      const result = await apiClient.retrainModel()
      toast({
        title: 'Model Retraining',
        description: result.message || 'Model retraining has been triggered. This may take several minutes.',
      })
    } catch (error: any) {
      toast({
        title: 'Retraining Failed',
        description: error.response?.data?.detail || 'Failed to trigger model retraining',
        variant: 'destructive',
      })
    } finally {
      setRetraining(false)
    }
  }

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Admin Panel</h1>
              <p className="text-white/70">Manage nodes, users, and ML models</p>
            </div>
            <Settings className="h-8 w-8 text-green-400" />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Node Management */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-green-400" />
                  <CardTitle className="text-white">Node Management</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {nodes && Array.isArray(nodes) && nodes.length > 0 ? (
                    nodes.map((node, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/20 rounded-lg">
                        <div>
                          <p className="font-semibold text-white">{node.name}</p>
                          <p className="text-sm text-white/70">{node.address}</p>
                        </div>
                        <div className={`h-3 w-3 rounded-full ${node.status === 'online' ? 'bg-green-500' : 'bg-green-700'}`}></div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-white/70">No nodes available</div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* User Roles */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-green-400" />
                  <CardTitle className="text-white">User Roles</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {users && Array.isArray(users) && users.length > 0 ? (
                    users.map((user, idx) => (
                      <div key={idx} className="p-3 bg-green-950/30 rounded-lg border border-green-500/20">
                        <p className="font-semibold text-white">{user.username}</p>
                        <p className="text-sm text-white/70">{user.email}</p>
                        <p className="text-xs text-white/60 mt-1">Role: {user.role}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-white/70">No users available</div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* ML Model Management */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-green-400" />
                  <CardTitle className="text-white">ML Model Management</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-green-950/30 rounded-lg border border-green-500/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-white">Model Status</span>
                      <span className="text-sm text-green-400 font-semibold">Trained</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-white/70">Accuracy</span>
                      <span className="text-sm font-semibold text-white">95.2%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-white/70">Last Trained</span>
                      <span className="text-sm text-white">2 hours ago</span>
                    </div>
                  </div>
                  <Button
                    onClick={handleRetrainModel}
                    disabled={retraining}
                    className="w-full"
                    variant="outline"
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${retraining ? 'animate-spin' : ''}`} />
                    {retraining ? 'Retraining...' : 'Trigger Model Retraining'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* System Status */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-green-400" />
                  <CardTitle className="text-white">System Status</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/20 rounded-lg">
                    <span className="text-sm font-semibold text-white">Backend API</span>
                    <span className="text-sm text-green-400 font-semibold">Online</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/20 rounded-lg">
                    <span className="text-sm font-semibold text-white">Database</span>
                    <span className="text-sm text-green-400 font-semibold">Connected</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/20 rounded-lg">
                    <span className="text-sm font-semibold text-white">Blockchain Network</span>
                    <span className="text-sm text-green-400 font-semibold">Active</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/20 rounded-lg">
                    <span className="text-sm font-semibold text-white">ML Service</span>
                    <span className="text-sm text-green-400 font-semibold">Ready</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

