'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings, Users, Server, Brain, RefreshCw, Shield, UserPlus, Mail, User, Lock, LogOut } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function AdminPage() {
  const [loading, setLoading] = useState(false)
  const [retraining, setRetraining] = useState(false)
  const [creatingUser, setCreatingUser] = useState(false)
  const [nodes, setNodes] = useState<any[]>([])
  const [users, setUsers] = useState<any[]>([])
  const [authenticated, setAuthenticated] = useState(false)
  const [newUser, setNewUser] = useState({
    email: '',
    username: '',
    password: '',
    role: '',
    organization: ''
  })
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
      const userData = JSON.parse(user)
      if (userData.role !== 'ADMIN') {
        toast({
          title: 'Access Denied',
          description: 'Admin access required.',
          variant: 'destructive',
        })
        router.push('/verifier')
        return
      }
      
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
      fetchNodes()
      fetchUsers()
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }, [router, toast])

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

  const handleLogout = async () => {
    await apiClient.logout()
    router.push('/login')
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreatingUser(true)

    try {
      const result = await apiClient.createUser(newUser)
      toast({
        title: 'User Created',
        description: `${result.username} (${result.role}) has been created successfully.`,
      })
      setNewUser({
        email: '',
        username: '',
        password: '',
        role: '',
        organization: ''
      })
      fetchUsers() // Refresh user list
    } catch (error: any) {
      toast({
        title: 'User Creation Failed',
        description: error.response?.data?.detail || 'Failed to create user',
        variant: 'destructive',
      })
    } finally {
      setCreatingUser(false)
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
              <p className="text-white/70">System administration: users, nodes, ML models & blockchain</p>
            </div>
            <div className="flex items-center gap-4">
              <Settings className="h-8 w-8 text-green-400" />
              <Button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
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

            {/* User Management */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-green-400" />
                  <CardTitle className="text-white">User Management</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                {/* Create User Form */}
                <form onSubmit={handleCreateUser} className="space-y-4 mb-6 p-4 bg-green-950/20 rounded-lg border border-green-500/20">
                  <h3 className="text-white font-semibold flex items-center gap-2">
                    <UserPlus className="h-4 w-4" />
                    Create New User
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="username" className="text-gray-300">Username</Label>
                      <Input
                        id="username"
                        value={newUser.username}
                        onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                        required
                        className="bg-gray-800 border-gray-600 text-white"
                        placeholder="Enter username"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-gray-300">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={newUser.email}
                        onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                        required
                        className="bg-gray-800 border-gray-600 text-white"
                        placeholder="Enter email"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="password" className="text-gray-300">Password</Label>
                      <Input
                        id="password"
                        type="password"
                        value={newUser.password}
                        onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                        required
                        className="bg-gray-800 border-gray-600 text-white"
                        placeholder="Enter password"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="role" className="text-gray-300">Role</Label>
                      <Select
                        id="role"
                        value={newUser.role}
                        onValueChange={(value) => setNewUser({...newUser, role: value})}
                        className="bg-gray-800 border-gray-600 text-white"
                      >
                        <option value="">Select role</option>
                        <SelectItem value="UPLOADER">Uploader</SelectItem>
                        <SelectItem value="VALIDATOR">Validator</SelectItem>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="organization" className="text-gray-300">Organization (Optional)</Label>
                    <Input
                      id="organization"
                      value={newUser.organization}
                      onChange={(e) => setNewUser({...newUser, organization: e.target.value})}
                      className="bg-gray-800 border-gray-600 text-white"
                      placeholder="Enter organization"
                    />
                  </div>
                  
                  <Button
                    type="submit"
                    disabled={creatingUser}
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                  >
                    {creatingUser ? 'Creating...' : 'Create User'}
                  </Button>
                </form>

                {/* Existing Users List */}
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  <h3 className="text-white font-semibold">Existing Users</h3>
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

