'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Eye, Calendar, User, CheckCircle, AlertCircle, Clock, Filter, Search, Trash2, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'

interface Trial {
  trial_id: string
  filename: string
  status: string
  participant_count?: number
  ml_status?: string
  blockchain_status?: string
  created_at: string
  ipfs_hash?: string
  uploaded_by?: string
  uploader_name?: string
}

export default function FilesPage() {
  const [trials, setTrials] = useState<Trial[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [authenticated, setAuthenticated] = useState(false)
  const [downloading, setDownloading] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [currentUser, setCurrentUser] = useState<any>(null)
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
      setCurrentUser(userData)
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
      fetchTrials()
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }, [])

  const fetchTrials = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getAllTrials()
      // API returns array directly, not object with trials property
      setTrials(Array.isArray(data) ? data : [])
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch files',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadReport = async (trialId: string) => {
    try {
      setDownloading(trialId)
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
        title: 'Success',
        description: 'Report downloaded successfully',
      })
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to download report',
        variant: 'destructive',
      })
    } finally {
      setDownloading(null)
    }
  }

  const handleViewFile = async (trial: Trial) => {
    // Check authentication before viewing
    const token = localStorage.getItem('token')
    if (!token) {
      toast({
        title: 'Authentication Required',
        description: 'Please login to view files',
        variant: 'destructive',
      })
      router.push('/login')
      return
    }
    
    try {
      // Download the CSV file for viewing
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/trials/${trial.trial_id}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.status === 401) {
        toast({
          title: 'Session Expired',
          description: 'Please login again',
          variant: 'destructive',
        })
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
        return
      }
      
      if (!response.ok) throw new Error('Failed to download file')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = trial.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: 'Success',
        description: 'File downloaded successfully',
      })
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to download file',
        variant: 'destructive',
      })
    }
  }

  const handleDeleteTrial = async (trial: Trial) => {
    if (!confirm(`Are you sure you want to delete ${trial.filename}? This action cannot be undone.`)) {
      return
    }

    try {
      setDeleting(trial.trial_id)
      await apiClient.deleteTrial(trial.trial_id)
      
      toast({
        title: 'Success',
        description: 'Trial deleted successfully',
      })
      
      // Refresh the trials list
      fetchTrials()
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete trial',
        variant: 'destructive',
      })
    } finally {
      setDeleting(null)
    }
  }

  const canDeleteTrial = (trial: Trial) => {
    if (!currentUser) return false
    // ONLY Admin can delete trials (blockchain deletion required)
    if (currentUser.role === 'ADMIN') return true
    return false
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
      })
    } catch (e) {
      return dateString
    }
  }

  const filteredTrials = trials.filter(trial => {
    // For validators, only show ACCEPT and REVIEW trials (exclude REJECT)
    if (currentUser?.role === 'VALIDATOR') {
      const isValidStatus = trial.ml_status === 'ACCEPT' || trial.ml_status === 'REVIEW'
      if (!isValidStatus) return false
    }
    
    const matchesSearch = trial.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         trial.trial_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || trial.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return <FileText className="h-5 w-5 text-blue-500" />
    }
  }

  const getStatusBadgeColor = (mlStatus: string) => {
    switch (mlStatus) {
      case 'ACCEPT':
        return 'bg-green-900/30 text-green-400 border-green-500/30'
      case 'REVIEW':
        return 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30'
      case 'REJECT':
        return 'bg-red-900/30 text-red-400 border-red-500/30'
      default:
        return 'bg-blue-900/30 text-blue-400 border-blue-500/30'
    }
  }
  
  const getCardBgColor = (mlStatus: string) => {
    switch (mlStatus) {
      case 'ACCEPT':
        return 'bg-green-950/20 border-green-500/40 hover:border-green-500/70'
      case 'REVIEW':
        return 'bg-yellow-950/20 border-yellow-500/40 hover:border-yellow-500/70'
      case 'REJECT':
        return 'bg-red-950/20 border-red-500/40 hover:border-red-500/70'
      default:
        return 'bg-gray-950/20 border-gray-500/40 hover:border-gray-500/70'
    }
  }

  return (
    <div className="min-h-screen bg-black py-12 relative overflow-hidden">
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-green-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-green-600 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000"></div>
      </div>

      <div className="container mx-auto px-4 max-w-6xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-5xl font-bold text-white mb-2">File Management</h1>
              <p className="text-white/70 text-lg">Access and manage your clinical trial files</p>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-green-500 rounded-2xl blur-lg opacity-50 animate-pulse"></div>
              <div className="relative bg-green-600 p-4 rounded-2xl">
                <FileText className="h-12 w-12 text-white" />
              </div>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <div className="relative glass">
              <Search className="absolute left-4 top-4 h-5 w-5 text-green-400" />
              <Input
                placeholder="Search by filename or trial ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 h-14 bg-white/10 border-white/30 text-white placeholder:text-white/60 backdrop-blur-xl focus:border-green-400 focus:ring-2 focus:ring-green-400/50 transition-all"
              />
            </div>
            <div className="flex gap-3 glass p-2 rounded-lg">
              <Filter className="h-5 w-5 text-green-400 my-auto ml-2" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex-1 px-4 py-2 bg-white/10 border border-white/30 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400 backdrop-blur-xl transition-all"
              >
                <option value="all" className="bg-black">All Status</option>
                <option value="processed" className="bg-black">Processed</option>
                <option value="pending" className="bg-black">Pending</option>
                <option value="failed" className="bg-black">Failed</option>
              </select>
            </div>
          </div>

          {/* Files List */}
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block relative">
                <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse"></div>
                <div className="relative h-16 w-16 border-4 border-white/20 border-t-green-500 rounded-full animate-spin"></div>
              </div>
              <p className="text-white/80 mt-6 text-lg">Loading files...</p>
            </div>
          ) : filteredTrials.length === 0 ? (
            <Card className="glass border-white/20 backdrop-blur-xl">
              <CardContent className="pt-16 pb-16 text-center">
                <div className="relative inline-block mb-6">
                  <div className="absolute inset-0 bg-green-500 rounded-full blur-2xl opacity-30"></div>
                  <FileText className="relative h-20 w-20 text-white/40" />
                </div>
                <p className="text-white/70 text-xl font-medium">No files found</p>
                <p className="text-white/50 mt-2">Try adjusting your search or filters</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {filteredTrials.map((trial) => (
                <motion.div
                  key={trial.trial_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  whileHover={{ scale: 1.01 }}
                >
                  <Card className={`glass backdrop-blur-xl transition-all duration-300 group border-2 ${getCardBgColor(trial.ml_status || 'pending')}`}>
                    <CardContent className="p-6">
                      <div className="grid lg:grid-cols-5 gap-4 items-center">
                        {/* File Info */}
                        <div className="lg:col-span-2 flex gap-4">
                          <div className="flex items-center">
                            <div className="relative">
                              <div className="absolute inset-0 bg-green-500 rounded-lg blur opacity-50 group-hover:opacity-75 transition-opacity"></div>
                              <div className="relative bg-white/10 p-3 rounded-lg">
                                {getStatusIcon(trial.status)}
                              </div>
                            </div>
                          </div>
                          <div className="flex-1">
                            <h3 className="text-white font-bold text-lg mb-1 group-hover:text-green-300 transition-colors">{trial.filename}</h3>
                            <p className="text-white/60 text-sm font-mono bg-black/30 px-2 py-1 rounded inline-block">{trial.trial_id}</p>
                            {trial.participant_count && (
                              <p className="text-white/60 text-sm mt-2">
                                <User className="inline h-3 w-3 mr-1" />
                                {trial.participant_count} participants
                              </p>
                            )}
                            {trial.uploader_name && (
                              <p className="text-green-400 text-xs mt-1">
                                Uploaded by: {trial.uploader_name}
                              </p>
                            )}
                            {/* ML Status Badge */}
                            {trial.ml_status && (
                              <div className="mt-2">
                                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadgeColor(trial.ml_status)}`}>
                                  ML: {trial.ml_status}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Upload Status Badge */}
                        <div className="flex justify-center">
                          <span className={`px-4 py-2 rounded-full text-sm font-bold border-2 ${trial.status === 'processed' ? 'bg-blue-900/30 text-blue-400 border-blue-500/30' : trial.status === 'pending' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30' : 'bg-red-900/30 text-red-400 border-red-500/30'} backdrop-blur-sm shadow-lg`}>
                            {trial.status.charAt(0).toUpperCase() + trial.status.slice(1)}
                          </span>
                        </div>

                        {/* Date */}
                        <div className="flex items-center gap-2 text-white/70 text-sm bg-black/20 px-3 py-2 rounded-lg">
                          <Calendar className="h-4 w-4 text-green-400" />
                          <span className="font-medium">{formatDate(trial.created_at)}</span>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 justify-end flex-wrap">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewFile(trial)}
                            className="text-green-400 border-green-400/50 hover:bg-green-600 hover:text-white hover:border-green-400 transition-all duration-300 shadow-lg hover:shadow-green-500/50"
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadReport(trial.trial_id)}
                            disabled={downloading === trial.trial_id}
                            className="text-green-300 border-green-300/50 hover:bg-green-500 hover:text-white hover:border-green-300 transition-all duration-300 shadow-lg hover:shadow-green-400/50"
                          >
                            <Download className="h-4 w-4 mr-1" />
                            {downloading === trial.trial_id ? 'Downloading...' : 'Report'}
                          </Button>
                          {canDeleteTrial(trial) && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteTrial(trial)}
                              disabled={deleting === trial.trial_id}
                              className="text-red-400 border-red-400/50 hover:bg-red-600 hover:text-white hover:border-red-400 transition-all duration-300 shadow-lg hover:shadow-red-500/50"
                            >
                              <Trash2 className="h-4 w-4 mr-1" />
                              {deleting === trial.trial_id ? 'Deleting...' : 'Delete'}
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}

          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <Card className="glass border-white/20 backdrop-blur-xl hover:border-green-400/50 transition-all duration-300 group">
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <div className="relative inline-block mb-3">
                    <div className="absolute inset-0 bg-green-500 rounded-full blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                    <FileText className="relative h-10 w-10 text-white" />
                  </div>
                  <p className="text-white/70 text-sm mb-2 font-medium">Total Files</p>
                  <p className="text-5xl font-bold text-green-400">{trials.length}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="glass border-white/20 backdrop-blur-xl hover:border-green-400/50 transition-all duration-300 group">
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <div className="relative inline-block mb-3">
                    <div className="absolute inset-0 bg-green-500 rounded-full blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                    <CheckCircle className="relative h-10 w-10 text-green-400" />
                  </div>
                  <p className="text-white/70 text-sm mb-2 font-medium">Processed</p>
                  <p className="text-5xl font-bold text-green-400">{trials.filter(t => t.status === 'processed').length}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="glass border-white/20 backdrop-blur-xl hover:border-green-400/50 transition-all duration-300 group">
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <div className="relative inline-block mb-3">
                    <div className="absolute inset-0 bg-green-500 rounded-full blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                    <Clock className="relative h-10 w-10 text-green-400" />
                  </div>
                  <p className="text-white/70 text-sm mb-2 font-medium">Pending</p>
                  <p className="text-5xl font-bold text-green-400">{trials.filter(t => t.status === 'pending').length}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
