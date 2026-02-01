'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, FileText, AlertTriangle, Search, Filter, LogOut, Eye, X, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'
import { formatDate } from '@/lib/date-utils'

interface Trial {
  trial_id: string
  filename: string
  status: string
  participant_count?: number
  ml_status?: string
  blockchain_status?: string
  blockchain_verified?: boolean
  created_at: string
}

export default function VerifierDashboard() {
  const [trials, setTrials] = useState<Trial[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [authenticated, setAuthenticated] = useState(false)
  const [verifying, setVerifying] = useState<string | null>(null)
  const [csvModalOpen, setCsvModalOpen] = useState(false)
  const [csvData, setCsvData] = useState<any[]>([])
  const [csvHeaders, setCsvHeaders] = useState<string[]>([])
  const [loadingCsv, setLoadingCsv] = useState(false)
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
      // Validators can access this page
      if (userData.role === 'UPLOADER' || userData.role === 'ADMIN') {
        // Uploaders and admins can also view trials
      } else if (userData.role !== 'VALIDATOR') {
        toast({
          title: 'Access Denied',
          description: 'You do not have permission to view this page.',
          variant: 'destructive',
        })
        router.push('/login')
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
      fetchTrials()
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }, []) // Remove router and toast from dependencies to prevent re-runs

  const fetchTrials = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getAllTrials()
      // API returns array directly, not object with trials property
      setTrials(Array.isArray(data) ? data : [])
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to fetch trials',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    apiClient.logout()
    router.push('/login')
  }

  const handleOpenFile = async (trialId: string) => {
    try {
      setLoadingCsv(true)
      const response = await apiClient.getTrialCsvData(trialId)
      if (response.data && response.headers) {
        setCsvHeaders(response.headers)
        setCsvData(response.data)
        setCsvModalOpen(true)
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load CSV file',
        variant: 'destructive',
      })
    } finally {
      setLoadingCsv(false)
    }
  }

  const handleVerifyTrial = async (trialId: string) => {
    if (!confirm('Verify and process this trial? This will write to blockchain and mark as verified.')) {
      return
    }
    
    try {
      setVerifying(trialId)
      
      // Step 1: Write to blockchain first
      try {
        const writeResult = await apiClient.writeToBlockchain(trialId)
        toast({
          title: 'Blockchain Write Success',
          description: `Trial written to blockchain. TX: ${writeResult.tx_hash.substring(0, 20)}...`,
        })
      } catch (writeError: any) {
        // If blockchain write fails, still try to verify
        console.error('Blockchain write error:', writeError)
        if (writeError.response?.status !== 400) {
          throw writeError
        }
      }
      
      // Step 2: Run blockchain verification
      const result = await apiClient.verifyBlockchain(trialId)
      
      if (result.tamper_detected) {
        toast({
          title: 'Tampering Detected!',
          description: 'This trial has been tampered with. Regulatory alert triggered.',
          variant: 'destructive',
        })
      } else {
        // Mark trial as verified locally
        setTrials(prev => prev.map(t => 
          t.trial_id === trialId 
            ? { ...t, blockchain_verified: true, blockchain_status: 'verified' }
            : t
        ))
        
        toast({
          title: 'Verification Complete',
          description: 'Trial verified successfully and stored on blockchain. Status: VERIFIED',
        })
      }
      
      // Refresh trials list to show updated status
      fetchTrials()
    } catch (error: any) {
      toast({
        title: 'Verification Failed',
        description: error.response?.data?.detail || 'Could not verify trial. It may need ML analysis first.',
        variant: 'destructive',
      })
    } finally {
      setVerifying(null)
    }
  }

  const filteredTrials = trials.filter(trial => {
    // Only show ACCEPT and REVIEW trials to validators (exclude REJECT)
    const isValidStatus = trial.ml_status === 'ACCEPT' || trial.ml_status === 'REVIEW'
    if (!isValidStatus) return false
    
    const matchesSearch = trial.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         trial.trial_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || trial.ml_status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (mlStatus: string) => {
    switch (mlStatus) {
      case 'ACCEPT': return 'bg-green-500'
      case 'REVIEW': return 'bg-yellow-500'
      case 'REJECT': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }
  
  const getStatusBgColor = (mlStatus: string) => {
    switch (mlStatus) {
      case 'ACCEPT': return 'bg-green-950/30 border-green-500/50'
      case 'REVIEW': return 'bg-yellow-950/30 border-yellow-500/50'
      case 'REJECT': return 'bg-red-950/30 border-red-500/50'
      default: return 'bg-gray-950/30 border-gray-500/50'
    }
  }

  const getStatusIcon = (mlStatus: string) => {
    switch (mlStatus) {
      case 'ACCEPT': return <CheckCircle className="h-4 w-4 text-white" />
      case 'REVIEW': return <AlertTriangle className="h-4 w-4 text-white" />
      case 'REJECT': return <FileText className="h-4 w-4 text-white" />
      default: return <FileText className="h-4 w-4 text-white" />
    }
  }

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="container mx-auto px-4 max-w-7xl">
        <div
          className="space-y-6"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Trial Verification</h1>
              <p className="text-white/70">Review and validate clinical trial data integrity</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all duration-200"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
              <CheckCircle className="h-12 w-12 text-green-400" />
            </div>
          </div>

          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search trials by filename or ID..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-gray-800 border-gray-600 text-white"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant={statusFilter === 'all' ? 'default' : 'outline'}
                    onClick={() => setStatusFilter('all')}
                    className="border-gray-600"
                  >
                    All
                  </Button>
                  <Button
                    variant={statusFilter === 'ACCEPT' ? 'default' : 'outline'}
                    onClick={() => setStatusFilter('ACCEPT')}
                    className="border-gray-600"
                  >
                    Accepted
                  </Button>
                  <Button
                    variant={statusFilter === 'REVIEW' ? 'default' : 'outline'}
                    onClick={() => setStatusFilter('REVIEW')}
                    className="border-gray-600"
                  >
                    Review
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Trials List */}
          <div className="grid gap-4">
            {loading ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center text-gray-400">Loading trials...</div>
                </CardContent>
              </Card>
            ) : filteredTrials.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center text-gray-400">No trials found</div>
                </CardContent>
              </Card>
            ) : (
              filteredTrials.map((trial, index) => (
                <div
                  key={trial.trial_id}
                >
                  <Card className={`hover:shadow-lg transition-all border-2 ${getStatusBgColor(trial.ml_status || 'pending')}`}>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-lg ${getStatusColor(trial.ml_status || 'pending')}`}>
                            {getStatusIcon(trial.ml_status || 'pending')}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-white">{trial.filename}</h3>
                            <p className="text-sm text-gray-400">ID: {trial.trial_id}</p>
                            <p className="text-sm text-white/80">
                              Participants: {trial.participant_count || 'N/A'} |
                              <span className={`font-bold ml-1 ${
                                trial.ml_status === 'ACCEPT' ? 'text-green-400' :
                                trial.ml_status === 'REVIEW' ? 'text-yellow-400' :
                                trial.ml_status === 'REJECT' ? 'text-red-400' : 'text-gray-400'
                              }`}>
                                ML: {trial.ml_status || 'Pending'}
                              </span> |
                              Blockchain: {trial.blockchain_status || 'Pending'}
                            </p>
                              <p className="text-sm text-gray-500 mt-2">
                                Uploaded: {formatDate(trial.created_at)}
                              </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold ${
                            trial.ml_status === 'ACCEPT' ? 'border-green-500 bg-green-500/20 text-green-300' :
                            trial.ml_status === 'REVIEW' ? 'border-yellow-500 bg-yellow-500/20 text-yellow-300' :
                            trial.ml_status === 'REJECT' ? 'border-red-500 bg-red-500/20 text-red-300' :
                            'border-gray-500 bg-gray-500/20 text-gray-300'
                          }`}>
                            {trial.ml_status || trial.status || 'PENDING'}
                          </span>
                          {trial.blockchain_verified && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 border border-green-500 rounded-full text-xs text-green-300">
                              <CheckCircle2 className="h-3 w-3" />
                              Verified
                            </span>
                          )}
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="border-purple-600 text-purple-400 hover:bg-purple-600/10"
                            onClick={() => handleOpenFile(trial.trial_id)}
                            disabled={loadingCsv}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            {loadingCsv ? 'Loading...' : 'Open File'}
                          </Button>
                          <Button variant="outline" size="sm" className="border-gray-600" onClick={async () => {
                            try {
                              const blob = await apiClient.downloadReport(trial.trial_id)
                              const url = window.URL.createObjectURL(blob)
                              window.open(url, '_blank')
                              toast({ title: 'Report Opened', description: 'PDF report opened in new tab' })
                            } catch (error: any) {
                              toast({ title: 'Error', description: 'Failed to open report', variant: 'destructive' })
                            }
                          }}>
                            View Report
                          </Button>
                          {!trial.blockchain_verified && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="border-blue-600 text-blue-400 hover:bg-blue-600/10"
                              disabled={verifying === trial.trial_id}
                              onClick={() => handleVerifyTrial(trial.trial_id)}
                            >
                              {verifying === trial.trial_id ? 'Verifying...' : 'Verify Trial'}
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            className="border-green-600 text-green-400"
                            onClick={async () => {
                              try {
                                const blob = await apiClient.downloadReport(trial.trial_id)
                                const url = window.URL.createObjectURL(blob)
                                const a = document.createElement('a')
                                a.href = url
                                a.download = `trial_report_${trial.trial_id}.pdf`
                                document.body.appendChild(a)
                                a.click()
                                window.URL.revokeObjectURL(url)
                                document.body.removeChild(a)
                                toast({ title: 'Report downloaded', description: 'PDF saved successfully.' })
                              } catch (error: any) {
                                toast({ title: 'Download failed', description: error.response?.data?.detail || 'Could not download report', variant: 'destructive' })
                              }
                            }}
                          >
                            Download Report
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* CSV Modal */}
      {csvModalOpen && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setCsvModalOpen(false)}>
          <div className="bg-gray-900 rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-xl font-bold text-white">CSV File Viewer</h2>
              <button onClick={() => setCsvModalOpen(false)} className="text-gray-400 hover:text-white">
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="overflow-auto max-h-[calc(90vh-80px)] p-4">
              <table className="w-full text-sm text-left text-gray-300">
                <thead className="text-xs text-gray-400 uppercase bg-gray-800 sticky top-0">
                  <tr>
                    {csvHeaders.map((header, idx) => (
                      <th key={idx} className="px-4 py-3">{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {csvData.map((row, rowIdx) => (
                    <tr key={rowIdx} className="border-b border-gray-700 hover:bg-gray-800/50">
                      {csvHeaders.map((header, colIdx) => (
                        <td key={colIdx} className="px-4 py-3">{row[header] || '-'}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}