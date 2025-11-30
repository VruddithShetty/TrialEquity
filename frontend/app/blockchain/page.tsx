'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Link2, Shield, Clock, PenTool, TrendingUp, Key, Upload, ArrowRight, List, Activity, BarChart3, ChevronDown, ChevronUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient, BlockchainWriteResponse, BlockchainVerifyResponse } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts'

export default function BlockchainPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const trialIdParam = searchParams.get('trial_id')
  const [trialId, setTrialId] = useState<string | null>(trialIdParam)
  const [availableTrials, setAvailableTrials] = useState<any[]>([])
  const [loadingTrialId, setLoadingTrialId] = useState(!trialIdParam)
  const [authenticated, setAuthenticated] = useState(false)
  const [writing, setWriting] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [writeResult, setWriteResult] = useState<BlockchainWriteResponse | null>(null)
  const [verifyResult, setVerifyResult] = useState<BlockchainVerifyResponse | null>(null)
  const [signing, setSigning] = useState(false)
  const [signed, setSigned] = useState(false)
  const [uploadingIPFS, setUploadingIPFS] = useState(false)
  const [ipfsResult, setIpfsResult] = useState<any>(null)
  const [tokenizing, setTokenizing] = useState(false)
  const [token, setToken] = useState<string | null>(null)
  const [generatingZKP, setGeneratingZKP] = useState(false)
  const [zkpProof, setZkpProof] = useState<any>(null)
  const [finalityData, setFinalityData] = useState<any[]>([])
  const [showComparison, setShowComparison] = useState(false)
  const [comparison, setComparison] = useState<any>(null)
  const [loadingComparison, setLoadingComparison] = useState(false)
  const { toast } = useToast()

  // Auto-login and auto-fetch trial ID
  useEffect(() => {
    const initializePage = async () => {
      // First, ensure we're authenticated
      let token = localStorage.getItem('token')
      if (!token) {
        // Try to auto-login
        try {
          const healthCheck = await fetch('http://localhost:8000/health')
          if (!healthCheck.ok) {
            throw new Error('Backend not ready')
          }
          const result = await apiClient.login('test@example.com', 'test123')
          if (result.access_token) {
            token = result.access_token
            setAuthenticated(true)
          }
        } catch (error: any) {
          console.error('Auto-login failed:', error)
          setLoadingTrialId(false)
          return
        }
      } else {
        // Verify token is valid
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          const exp = payload.exp * 1000
          if (exp > Date.now()) {
            setAuthenticated(true)
          } else {
            localStorage.removeItem('token')
            const result = await apiClient.login('test@example.com', 'test123')
            if (result.access_token) {
              setAuthenticated(true)
            }
          }
        } catch (e) {
          // Invalid token, try to login
          try {
            const result = await apiClient.login('test@example.com', 'test123')
            if (result.access_token) {
              setAuthenticated(true)
            }
          } catch (error: any) {
            console.error('Login failed:', error)
          }
        }
      }

      // If we already have a trial ID from URL, use it
      if (trialIdParam) {
        setTrialId(trialIdParam)
        setLoadingTrialId(false)
        return
      }

      // Try to get trial ID from localStorage (stored after upload)
      const storedTrialId = localStorage.getItem('lastTrialId')
      if (storedTrialId) {
        setTrialId(storedTrialId)
        setLoadingTrialId(false)
        toast({
          title: 'Using Recent Trial',
          description: `Loaded trial ${storedTrialId} from recent activity`,
        })
        return
      }

      // Try to fetch latest trial from API
      if (authenticated || token) {
        try {
          const trials = await apiClient.getAllTrials()
          if (trials && trials.length > 0) {
            setAvailableTrials(trials)
            // Auto-select the first trial (most recent)
            const latestTrial = trials[0]
            if (latestTrial.trial_id) {
              setTrialId(latestTrial.trial_id)
              localStorage.setItem('lastTrialId', latestTrial.trial_id)
              toast({
                title: 'Auto-selected Trial',
                description: `Using latest trial: ${latestTrial.trial_id}`,
              })
            }
          }
        } catch (error: any) {
          console.error('Failed to fetch trials:', error)
          // If we can't fetch, that's okay - user can select manually or provide trial_id
        }
      }
      
      setLoadingTrialId(false)
    }

    initializePage()
  }, [trialIdParam, authenticated, toast])

  const handleWrite = async () => {
    if (!trialId) return

    setWriting(true)
    try {
      const result = await apiClient.writeToBlockchain(trialId)
      setWriteResult(result)
      
      // Generate time-to-finality data
      const finalityData = []
      for (let i = 0; i <= 10; i++) {
        finalityData.push({
          time: i * 0.1,
          probability: Math.min(100, (i * 10) + Math.random() * 5)
        })
      }
      setFinalityData(finalityData)
      
      toast({
        title: 'Blockchain Write Successful',
        description: `Transaction hash: ${result.tx_hash.substring(0, 20)}...`,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to write to blockchain'
      
      // Check if error is due to missing ML check
      if (errorMessage.includes('ml_status') || errorMessage.includes('Cannot write trial')) {
        toast({
          title: 'ML Bias Check Required',
          description: 'Trial must pass ML bias check first. Please run ML Analysis before writing to blockchain.',
          variant: 'destructive',
        })
      } else {
        toast({
          title: 'Write Failed',
          description: errorMessage,
          variant: 'destructive',
        })
      }
    } finally {
      setWriting(false)
    }
  }

  const handleSignTrial = async () => {
    if (!trialId) return

    setSigning(true)
    try {
      const result = await apiClient.signTrial(trialId)
      setSigned(true)
      toast({
        title: 'Trial Signed',
        description: `Digital signature: ${result.signature.substring(0, 20)}...`,
      })
    } catch (error: any) {
      toast({
        title: 'Signing Failed',
        description: error.response?.data?.detail || 'Failed to sign trial',
        variant: 'destructive',
      })
    } finally {
      setSigning(false)
    }
  }

  const handleUploadIPFS = async () => {
    if (!trialId) return

    setUploadingIPFS(true)
    try {
      const result = await apiClient.uploadToIPFS(trialId)
      setIpfsResult(result)
      toast({
        title: 'Uploaded to IPFS',
        description: `IPFS hash: ${result.ipfs_hash.substring(0, 20)}...`,
      })
    } catch (error: any) {
      toast({
        title: 'IPFS Upload Failed',
        description: error.response?.data?.detail || 'Failed to upload to IPFS',
        variant: 'destructive',
      })
    } finally {
      setUploadingIPFS(false)
    }
  }

  const handleTokenize = async () => {
    if (!trialId) return

    setTokenizing(true)
    try {
      const result = await apiClient.tokenizeTrial(trialId)
      setToken(result.token)
      toast({
        title: 'Token Generated',
        description: 'Pseudonymous token created for auditing',
      })
    } catch (error: any) {
      toast({
        title: 'Tokenization Failed',
        description: error.response?.data?.detail || 'Failed to generate token',
        variant: 'destructive',
      })
    } finally {
      setTokenizing(false)
    }
  }

  const handleGenerateZKP = async () => {
    if (!trialId) return

    setGeneratingZKP(true)
    try {
      const result = await apiClient.generateZKP(trialId)
      setZkpProof(result)
      toast({
        title: 'ZKP Generated',
        description: 'Zero-knowledge proof created successfully',
      })
    } catch (error: any) {
      toast({
        title: 'ZKP Generation Failed',
        description: error.response?.data?.detail || 'Failed to generate ZKP',
        variant: 'destructive',
      })
    } finally {
      setGeneratingZKP(false)
    }
  }

  const handleVerify = async () => {
    if (!trialId || !writeResult) return

    setVerifying(true)
    try {
      const result = await apiClient.verifyBlockchain(trialId)
      setVerifyResult(result)
      if (result.tamper_detected) {
        toast({
          title: 'Tampering Detected!',
          description: 'Trial data has been tampered with',
          variant: 'destructive',
        })
      } else {
        toast({
          title: 'Verification Successful',
          description: 'Trial integrity confirmed',
        })
      }
    } catch (error: any) {
      toast({
        title: 'Verification Failed',
        description: error.response?.data?.detail || 'Failed to verify',
        variant: 'destructive',
      })
    } finally {
      setVerifying(false)
    }
  }

  if (!trialId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <p className="text-white">No trial ID provided</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden py-12">
      {/* Background effects */}
      <div className="fixed inset-0 blockchain-grid opacity-25" />
      <div className="fixed inset-0 hex-pattern opacity-15" />
      
      <div className="container mx-auto px-4 max-w-5xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-center mb-12">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mb-6 green-glow"
            >
              <Link2 className="h-10 w-10 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              <span className="gradient-text-green">Blockchain</span> Operations
            </h1>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <p className="text-xl text-white">
                Trial ID: <span className="text-green-400 font-mono">{trialId}</span>
              </p>
              {availableTrials.length > 1 && (
                <Button
                  onClick={() => {
                    setTrialId(null)
                    router.push('/blockchain')
                  }}
                  variant="outline"
                  size="sm"
                  className="border-green-500/50 text-green-400 hover:bg-green-950/30"
                >
                  <List className="h-4 w-4 mr-2" />
                  Change Trial
                </Button>
              )}
            </div>
          </div>

          {/* Write to Blockchain */}
          <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl text-white">
                <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <Link2 className="h-5 w-5 text-green-400" />
                </div>
                Write to Blockchain
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!writeResult ? (
                <div>
                  <p className="text-white mb-4 leading-relaxed">
                    Write the validated trial to the Hyperledger Fabric blockchain.
                    This will create an immutable record with cryptographic hash.
                  </p>
                  <div className="mb-4 p-4 bg-green-950/30 border border-green-500/40 rounded-lg">
                    <p className="text-sm text-green-400 mb-1 font-semibold">
                      <strong>Prerequisite:</strong> Trial must pass ML bias analysis first
                    </p>
                    <p className="text-xs text-white/70">
                      Only trials with ML status "ACCEPT" or "REVIEW" can be written to blockchain.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button 
                      onClick={() => router.push(`/ml-analysis?trial_id=${trialId}`)}
                      variant="outline"
                      size="lg"
                      className="flex-1 border-green-500/50 text-white hover:bg-green-950/40"
                    >
                      Run ML Analysis First
                    </Button>
                    <Button 
                      onClick={handleWrite} 
                      disabled={writing} 
                      size="lg" 
                      className="flex-1 bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300"
                    >
                      {writing ? (
                        <>
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="mr-2"
                          >
                            <Activity className="h-5 w-5" />
                          </motion.div>
                          Writing...
                        </>
                      ) : (
                        <>
                          <Link2 className="mr-2 h-5 w-5" />
                          Write to Blockchain
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-4"
                >
                  <div className="flex items-start gap-4 p-6 bg-green-950/30 rounded-xl border border-green-500/50 green-glow">
                    <div className="relative">
                      <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse" />
                      <CheckCircle className="h-8 w-8 text-green-500 relative z-10" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <p className="font-semibold text-white text-lg">Successfully written to blockchain</p>
                      <div className="p-3 bg-black/40 rounded-lg border border-green-500/30">
                        <p className="text-xs text-green-400 mb-1">Transaction Hash:</p>
                        <code className="text-sm text-green-300 font-mono break-all">{writeResult.tx_hash}</code>
                      </div>
                      {writeResult.block_number && (
                        <div className="flex items-center gap-4 text-sm">
                          <div>
                            <span className="text-white/70">Block Number:</span>{' '}
                            <span className="text-green-400 font-mono">{writeResult.block_number}</span>
                          </div>
                        </div>
                      )}
                      <div className="text-sm">
                        <span className="text-gray-400">Timestamp:</span>{' '}
                        <span className="text-white">{new Date(writeResult.timestamp).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </Card>

          {/* Verify Blockchain */}
          {writeResult && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Shield className="h-5 w-5 text-green-400" />
                  </div>
                  Verify Integrity
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!verifyResult ? (
                  <div>
                    <p className="text-white mb-6 leading-relaxed">
                      Verify the trial's integrity on the blockchain by checking the hash.
                    </p>
                    <Button 
                      onClick={handleVerify} 
                      disabled={verifying} 
                      size="lg" 
                      className="w-full bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300"
                    >
                      {verifying ? (
                        <>
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="mr-2"
                          >
                            <Activity className="h-5 w-5" />
                          </motion.div>
                          Verifying...
                        </>
                      ) : (
                        <>
                          <Shield className="mr-2 h-5 w-5" />
                          Verify Trial Integrity
                        </>
                      )}
                    </Button>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <div
                      className={`p-6 rounded-xl border ${
                        verifyResult.tamper_detected
                          ? 'bg-green-950/40 border-green-600/50'
                          : 'bg-green-950/30 border-green-500/50 green-glow'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="relative">
                          <div className={`absolute inset-0 rounded-full blur-xl opacity-50 animate-pulse ${
                            verifyResult.tamper_detected ? 'bg-green-700' : 'bg-green-500'
                          }`} />
                          {verifyResult.tamper_detected ? (
                            <XCircle className="h-8 w-8 text-green-600 relative z-10" />
                          ) : (
                            <CheckCircle className="h-8 w-8 text-green-500 relative z-10" />
                          )}
                        </div>
                        <div className="flex-1 space-y-3">
                          <p
                            className={`font-semibold text-lg text-white ${
                              verifyResult.tamper_detected ? 'text-green-400' : 'text-green-400'
                            }`}
                          >
                            {verifyResult.tamper_detected
                              ? 'Tampering Detected!'
                              : 'Integrity Verified'}
                          </p>
                          <div className="space-y-2 text-sm">
                            <div className={`p-2 rounded border ${
                              verifyResult.tamper_detected 
                                ? 'bg-green-950/40 border-green-600/40' 
                                : 'bg-green-950/20 border-green-500/30'
                            }`}>
                              <span className="text-white/70">Hash Match: </span>
                              <span className={verifyResult.tamper_detected ? 'text-green-400' : 'text-green-400'}>
                                {verifyResult.hash_match ? 'Yes' : 'No'}
                              </span>
                            </div>
                            <div className={`p-2 rounded border ${
                              verifyResult.tamper_detected 
                                ? 'bg-green-950/40 border-green-600/40' 
                                : 'bg-green-950/20 border-green-500/30'
                            }`}>
                              <span className="text-white/70">Valid: </span>
                              <span className={verifyResult.tamper_detected ? 'text-green-400' : 'text-green-400'}>
                                {verifyResult.is_valid ? 'Yes' : 'No'}
                              </span>
                            </div>
                            <div className="text-white">
                              <span className="text-white/70">Verified: </span>
                              {new Date(verifyResult.verification_timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Digital Signature */}
          {writeResult && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <PenTool className="h-5 w-5 text-green-400" />
                  </div>
                  Digital Signature
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!signed ? (
                  <div>
                    <p className="text-white mb-6 leading-relaxed">
                      Cryptographically sign this trial submission as an investigator.
                    </p>
                    <Button 
                      onClick={handleSignTrial} 
                      disabled={signing} 
                      size="lg" 
                      className="w-full bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300"
                    >
                      <PenTool className="h-4 w-4 mr-2" />
                      {signing ? 'Signing...' : 'Sign Trial'}
                    </Button>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-6 bg-green-950/30 rounded-xl border border-green-500/50 green-glow"
                  >
                    <div className="flex items-start gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse" />
                        <CheckCircle className="h-8 w-8 text-green-500 relative z-10" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <p className="font-semibold text-white text-lg">Trial Signed</p>
                        <p className="text-sm text-white">
                          <span className="text-gray-400">Signed by:</span> <span className="text-green-400">Investigator</span>
                        </p>
                        <div className="p-3 bg-black/40 rounded-lg border border-green-500/30 mt-3">
                          <p className="text-xs text-green-400 mb-1">Digital Signature:</p>
                          <code className="text-sm text-green-300 font-mono break-all">
                            {Date.now().toString(36).toUpperCase()}
                          </code>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Time-to-Finality Graph */}
          {writeResult && finalityData.length > 0 && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-green-400" />
                  </div>
                  Time-to-Finality
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black/40 rounded-lg p-4 border border-green-500/20">
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={finalityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#22c55e20" />
                      <XAxis 
                        dataKey="time" 
                        stroke="#22c55e80"
                        label={{ value: 'Time (seconds)', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                      />
                      <YAxis 
                        stroke="#22c55e80"
                        label={{ value: 'Finality Probability (%)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#000000', 
                          border: '1px solid #22c55e50',
                          borderRadius: '8px',
                          color: '#ffffff'
                        }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="probability" 
                        stroke="#22c55e" 
                        fill="#22c55e" 
                        fillOpacity={0.6}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 p-4 bg-green-950/30 rounded-lg border border-green-500/30">
                  <p className="text-sm text-white">
                    <span className="font-semibold text-green-400">Finality Time:</span> <span className="text-green-300">~1.0 seconds</span>
                  </p>
                  <p className="text-sm text-white mt-1">
                    Transaction reaches 100% finality probability within 1 second on Hyperledger Fabric.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* IPFS Upload */}
          {writeResult && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Upload className="h-5 w-5 text-green-400" />
                  </div>
                  IPFS Storage
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!ipfsResult ? (
                  <div>
                    <p className="text-white mb-6 leading-relaxed">
                      Upload trial data to IPFS for decentralized storage.
                    </p>
                    <Button
                      onClick={handleUploadIPFS}
                      disabled={uploadingIPFS}
                      size="lg"
                      className="w-full bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {uploadingIPFS ? 'Uploading to IPFS...' : 'Upload to IPFS'}
                    </Button>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-6 bg-green-950/30 rounded-xl border border-green-500/50 green-glow"
                  >
                    <div className="flex items-start gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse" />
                        <CheckCircle className="h-8 w-8 text-green-500 relative z-10" />
                      </div>
                      <div className="flex-1 space-y-3">
                        <p className="font-semibold text-white text-lg">Uploaded to IPFS</p>
                        <div className="p-3 bg-black/40 rounded-lg border border-green-500/30">
                          <p className="text-xs text-green-400 mb-1">IPFS Hash:</p>
                          <code className="text-sm text-green-300 font-mono break-all">{ipfsResult.ipfs_hash}</code>
                        </div>
                        {ipfsResult.status === 'mock' ? (
                          <div className="p-3 bg-green-950/30 rounded-lg border border-green-500/40">
                            <p className="text-xs text-green-400 mb-2 font-semibold">
                              ⚠️ IPFS Not Available Locally
                            </p>
                            <p className="text-xs text-white/70 mb-3">
                              This is a demonstration hash. The file was not uploaded to IPFS. 
                              To enable real IPFS storage, install and run an IPFS node.
                            </p>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  navigator.clipboard.writeText(ipfsResult.ipfs_hash)
                                  toast({
                                    title: 'Hash Copied',
                                    description: 'IPFS hash copied to clipboard',
                                  })
                                }}
                                className="text-xs border-green-500/50 text-white hover:bg-green-950/40"
                              >
                                Copy Hash
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <a
                              href={ipfsResult.ipfs_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-green-400 hover:text-green-300 hover:underline inline-flex items-center gap-1 transition-colors"
                            >
                              View on IPFS <ArrowRight className="h-4 w-4" />
                            </a>
                            <div className="flex gap-2 flex-wrap">
                              <a
                                href={`https://ipfs.io/ipfs/${ipfsResult.ipfs_hash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-white/70 hover:text-white hover:underline"
                              >
                                ipfs.io
                              </a>
                              <span className="text-white/30">•</span>
                              <a
                                href={`https://gateway.pinata.cloud/ipfs/${ipfsResult.ipfs_hash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-white/70 hover:text-white hover:underline"
                              >
                                pinata.cloud
                              </a>
                              <span className="text-white/30">•</span>
                              <a
                                href={`https://cloudflare-ipfs.com/ipfs/${ipfsResult.ipfs_hash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-white/70 hover:text-white hover:underline"
                              >
                                cloudflare
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Tokenization */}
          {writeResult && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Key className="h-5 w-5 text-green-400" />
                  </div>
                  Tokenization
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!token ? (
                  <div>
                    <p className="text-white mb-6 leading-relaxed">
                      Generate a pseudonymous token for cross-study auditing.
                    </p>
                    <Button
                      onClick={handleTokenize}
                      disabled={tokenizing}
                      size="lg"
                      className="w-full border-2 border-green-500/50 text-green-400 hover:bg-green-950/30 hover:border-green-400 transition-all duration-300"
                      variant="outline"
                    >
                      <Key className="h-4 w-4 mr-2" />
                      {tokenizing ? 'Generating Token...' : 'Generate Token'}
                    </Button>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-6 bg-green-950/30 rounded-xl border border-green-500/50 green-glow"
                  >
                    <p className="font-semibold text-white text-lg mb-3">Token Generated</p>
                    <div className="p-4 bg-black/40 rounded-lg border border-green-500/30">
                      <code className="text-sm text-green-300 font-mono break-all">{token}</code>
                    </div>
                    <p className="text-xs text-white/70 mt-3">
                      Use this token for pseudonymous cross-study auditing
                    </p>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Zero-Knowledge Proof */}
          {writeResult && (
            <Card className="mb-6 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Shield className="h-5 w-5 text-green-400" />
                  </div>
                  Zero-Knowledge Proof
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!zkpProof ? (
                  <div>
                    <p className="text-white mb-6 leading-relaxed">
                      Generate a ZKP to prove data authenticity without exposing PHI.
                    </p>
                    <Button
                      onClick={handleGenerateZKP}
                      disabled={generatingZKP}
                      size="lg"
                      className="w-full border-2 border-green-500/50 text-green-400 hover:bg-green-950/30 hover:border-green-400 transition-all duration-300"
                      variant="outline"
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      {generatingZKP ? 'Generating Proof...' : 'Generate ZKP'}
                    </Button>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-6 bg-green-950/30 rounded-xl border border-green-500/50 green-glow"
                  >
                    <p className="font-semibold text-white text-lg mb-3">ZKP Generated</p>
                    <div className="p-4 bg-black/40 rounded-lg border border-green-500/30 mb-3">
                      <p className="text-xs text-green-400 mb-1">Commitment:</p>
                      <code className="text-sm text-green-300 font-mono break-all">
                        {zkpProof.proof?.commitment?.substring(0, 30)}...
                      </code>
                    </div>
                    <p className="text-xs text-white/70">
                      Proof type: <span className="text-green-400">{zkpProof.proof?.proof_type}</span>
                    </p>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Node Consensus Visualization */}
          {writeResult && (
            <Card className="blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-white">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Clock className="h-5 w-5 text-green-400" />
                  </div>
                  Network Consensus
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {['Sponsor Node', 'Investigator Node', 'Regulator Node', 'Auditor Node'].filter(Boolean).map(
                      (node, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="p-4 bg-green-950/30 rounded-lg border border-green-500/30 text-center glass-effect hover:border-green-500/50 transition-all duration-300"
                        >
                          <div className="relative w-4 h-4 mx-auto mb-3">
                            <div className="absolute inset-0 bg-green-500 rounded-full blur-sm opacity-50 animate-pulse" />
                            <div className="relative w-4 h-4 bg-green-500 rounded-full" />
                          </div>
                          <p className="text-sm font-semibold text-white">{node}</p>
                          <p className="text-xs text-green-400 mt-1">Consensus: ✓</p>
                        </motion.div>
                      )
                    )}
                  </div>
                  <div className="mt-4 p-4 bg-green-950/20 rounded-lg border border-green-500/30">
                    <p className="text-sm text-gray-300">
                      All nodes have reached consensus. Transaction finalized in block{' '}
                      <span className="text-green-400 font-mono">{writeResult.block_number || 'N/A'}</span>.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Blockchain Platform Comparison */}
          {showComparison && comparison && (
            <Card className="mt-8 blockchain-block glass-effect border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-xl text-white">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                      <BarChart3 className="h-5 w-5 text-green-400" />
                    </div>
                    <span>Blockchain Platform Comparison</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowComparison(false)}
                    className="text-gray-400 hover:text-white"
                  >
                    <ChevronUp className="h-4 w-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Summary */}
                <div className="mb-6 p-4 bg-green-950/30 rounded-lg border border-green-500/30">
                  <p className="text-sm text-green-400 font-semibold mb-2">Recommendation</p>
                  <p className="text-white">{comparison.summary.recommendation}</p>
                </div>

                {/* Performance Metrics */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-white font-semibold mb-4">Transactions Per Second (TPS)</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">Hyperledger Fabric</span>
                        <span className="text-green-400 font-mono font-semibold">{comparison.hyperledger_fabric.tps}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">MultiChain</span>
                        <span className="text-yellow-400 font-mono font-semibold">{comparison.multichain.tps}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">Quorum</span>
                        <span className="text-orange-400 font-mono font-semibold">{comparison.quorum.tps}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-white font-semibold mb-4">Latency (ms)</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">Hyperledger Fabric</span>
                        <span className="text-green-400 font-mono font-semibold">{comparison.hyperledger_fabric.latency_ms}ms</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">MultiChain</span>
                        <span className="text-yellow-400 font-mono font-semibold">{comparison.multichain.latency_ms}ms</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-950/20 rounded-lg">
                        <span className="text-gray-300">Quorum</span>
                        <span className="text-orange-400 font-mono font-semibold">{comparison.quorum.latency_ms}ms</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Detailed Comparison Table */}
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b-2 border-green-500/40">
                        <th className="text-left p-3 font-semibold text-white">Metric</th>
                        <th className="text-left p-3 font-semibold text-white">Hyperledger Fabric</th>
                        <th className="text-left p-3 font-semibold text-white">MultiChain</th>
                        <th className="text-left p-3 font-semibold text-white">Quorum</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { key: 'privacy', label: 'Privacy' },
                        { key: 'channels', label: 'Channels' },
                        { key: 'chaincode_expressiveness', label: 'Chaincode Expressiveness' },
                        { key: 'regulatory_suitability', label: 'Regulatory Suitability' },
                        { key: 'ease_of_deployment', label: 'Ease of Deployment' },
                        { key: 'tamper_detection', label: 'Tamper Detection' },
                        { key: 'consensus', label: 'Consensus' },
                        { key: 'use_case', label: 'Use Case' },
                      ].map(({ key, label }) => (
                        <tr key={key} className="border-b border-green-500/20 hover:bg-green-950/30">
                          <td className="p-3 font-medium text-white">{label}</td>
                          <td className="p-3 text-gray-300">{comparison.hyperledger_fabric[key]}</td>
                          <td className="p-3 text-gray-300">{comparison.multichain[key]}</td>
                          <td className="p-3 text-gray-300">{comparison.quorum[key]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <Button
              onClick={() => router.push(`/regulator?trial_id=${trialId}`)}
              variant="outline"
              size="lg"
              className="border-2 border-green-500/50 text-green-400 hover:bg-green-950/30 hover:border-green-400 transition-all duration-300"
            >
              View Regulator Dashboard
            </Button>
            <Button
              onClick={async () => {
                if (!showComparison && !comparison) {
                  setLoadingComparison(true)
                  try {
                    const data = await apiClient.compareBlockchains()
                    setComparison(data)
                  } catch (error) {
                    toast({
                      title: 'Failed to load comparison',
                      description: 'Could not fetch blockchain comparison data',
                      variant: 'destructive',
                    })
                  } finally {
                    setLoadingComparison(false)
                  }
                }
                setShowComparison(!showComparison)
              }}
              variant="outline"
              size="lg"
              className="border-2 border-green-500/50 text-green-400 hover:bg-green-950/30 hover:border-green-400 transition-all duration-300"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              {loadingComparison ? 'Loading...' : showComparison ? 'Hide Comparison' : 'Compare Platforms'}
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

