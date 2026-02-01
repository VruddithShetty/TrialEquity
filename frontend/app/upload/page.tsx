'use client'

import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, File, CheckCircle, AlertCircle, Shield, Play, Activity, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [validating, setValidating] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [validationResult, setValidationResult] = useState<any>(null)
  const [preprocessingPreview, setPreprocessingPreview] = useState<any>(null)
  const [authenticated, setAuthenticated] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (!token || !user) {
      router.push('/login')
      return
    }
    
    try {
      const userData = JSON.parse(user)
      // Check if user has upload permissions (ADMIN or UPLOADER)
      if (userData.role !== 'ADMIN' && userData.role !== 'UPLOADER') {
        toast({
          title: 'Access Denied',
          description: 'You do not have permission to upload trials.',
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
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }, [router, toast])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setUploadResult(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/xml': ['.xml'],
    },
    maxFiles: 1,
  })

  const handleUpload = async () => {
    if (!file) return
    
    // Check if we have a token
    const token = localStorage.getItem('token')
    if (!token || !authenticated) {
      toast({
        title: 'Authentication Required',
        description: 'Please login first.',
        variant: 'destructive',
      })
      router.push('/login')
      return
    }

    setUploading(true)
    try {
      const result = await apiClient.uploadTrial(file)
      setUploadResult(result)
      
      // Simulate preprocessing preview
      setPreprocessingPreview({
        filename: result.filename,
        participant_count: result.participant_count || 0,
        status: 'preprocessed',
        steps: [
          'File uploaded',
          'Data cleaned',
          'Normalized',
          'Pseudonymized',
          'Ready for validation'
        ]
      })
      
      toast({
        title: 'Upload Successful',
        description: `Trial ${result.trial_id} uploaded successfully`,
      })
      
      // Store trial ID in localStorage for auto-selection on other pages
      localStorage.setItem('lastTrialId', result.trial_id)
      
      // Navigate to ML analysis page
      setTimeout(() => {
        router.push(`/ml-analysis?trial_id=${result.trial_id}`)
      }, 1500)
    } catch (error: any) {
      console.error('Upload error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload trial'
      toast({
        title: 'Upload Failed',
        description: errorMessage,
        variant: 'destructive',
      })
      console.error('Full error:', error.response?.data || error)
    } finally {
      setUploading(false)
    }
  }

  const handleValidateRules = async () => {
    if (!uploadResult?.trial_id) return

    setValidating(true)
    try {
      const result = await apiClient.validateRules(uploadResult.trial_id)
      setValidationResult(result)
      toast({
        title: 'Validation Complete',
        description: `Status: ${result.status}`,
      })
    } catch (error: any) {
      toast({
        title: 'Validation Failed',
        description: error.response?.data?.detail || 'Failed to validate rules',
        variant: 'destructive',
      })
    } finally {
      setValidating(false)
    }
  }

  const handleLogout = () => {
    apiClient.logout()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden py-12">
      {/* Background effects */}
      <div className="fixed inset-0 blockchain-grid opacity-20" />
      <div className="fixed inset-0 hex-pattern opacity-15" />
      
      <div className="container mx-auto px-4 max-w-4xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-center mb-12">
            <div className="flex justify-end mb-4">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all duration-200"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-green-500 via-emerald-600 to-green-700 rounded-3xl mb-6 green-glow-intense relative group"
            >
              <Upload className="h-12 w-12 text-white drop-shadow-lg group-hover:scale-110 transition-transform" />
              <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-400 rounded-full animate-sparkle" />
            </motion.div>
            <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-4">
              Upload <span className="text-premium-gradient">Clinical Trial</span>
            </h1>
            <p className="text-xl text-white max-w-2xl mx-auto leading-relaxed">
              Upload your clinical trial dataset for advanced ML bias analysis 
              <br className="hidden md:block" />
              <span className="text-green-400">and secure blockchain storage</span>
            </p>
          </div>

          <Card className="mb-6 premium-card blockchain-block glass-effect-premium border-green-500/40 hover:border-green-500/70">
            <CardHeader>
              <CardTitle className="text-2xl md:text-3xl text-white flex items-center gap-3 text-premium-glow">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500/30 to-emerald-500/20 rounded-xl flex items-center justify-center green-glow">
                  <File className="h-6 w-6 text-green-400" />
                </div>
                File Upload
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-300 relative overflow-hidden group ${
                  isDragActive
                    ? 'border-green-500 bg-green-950/40 green-glow-intense scale-[1.02]'
                    : 'border-green-500/50 hover:border-green-500 hover:bg-green-950/30 hover:shadow-lg hover:shadow-green-500/20'
                }`}
              >
                <div className="absolute inset-0 animate-shimmer opacity-0 group-hover:opacity-100 transition-opacity" />
                <input {...getInputProps()} />
                <div className="relative z-10">
                  <motion.div
                    animate={{ 
                      scale: isDragActive ? 1.1 : 1,
                      rotate: isDragActive ? 5 : 0
                    }}
                    transition={{ duration: 0.2 }}
                  >
                    <Upload className="h-16 w-16 text-green-400 mx-auto mb-4" />
                  </motion.div>
                  {isDragActive ? (
                    <motion.p 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-green-400 text-xl font-semibold"
                    >
                      Drop the file here...
                    </motion.p>
                  ) : (
                    <div>
                      <p className="text-white mb-2 text-lg">
                        Drag and drop a file here, or click to select
                      </p>
                      <p className="text-sm text-white/70">
                        Supports CSV, JSON, XML formats
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {file && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 flex items-center gap-4 p-4 bg-green-950/30 border border-green-500/30 rounded-lg glass-effect"
                >
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <File className="h-6 w-6 text-green-400" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-white">{file.name}</p>
                    <p className="text-sm text-gray-400">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                </motion.div>
              )}

              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full mt-6 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300 btn-premium relative overflow-hidden group"
                size="lg"
              >
                {uploading ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="mr-2"
                    >
                      <Activity className="h-5 w-5" />
                    </motion.div>
                    Uploading to Blockchain...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-5 w-5" />
                    Upload Trial
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Preprocessing Preview */}
          {preprocessingPreview && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6"
            >
              <Card className="blockchain-block glass-effect border-green-500/30">
                <CardHeader>
                  <CardTitle className="text-xl text-white flex items-center gap-2">
                    <Activity className="h-5 w-5 text-green-400" />
                    Preprocessing Preview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {preprocessingPreview?.steps && Array.isArray(preprocessingPreview.steps) && preprocessingPreview.steps.map((step: string, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-center gap-3 p-3 bg-green-950/20 rounded-lg border border-green-500/20"
                      >
                        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                        <span className="text-sm text-white">{step}</span>
                      </motion.div>
                    ))}
                    <div className="mt-4 pt-4 border-t border-green-500/20">
                      <p className="text-sm text-white">
                        <span className="font-semibold text-green-400">Participants:</span>{' '}
                        <span className="text-white">{preprocessingPreview.participant_count}</span>
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {uploadResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-6"
            >
              <Card className="border-green-500/50 bg-green-950/30 glass-effect green-glow">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-green-500 rounded-full blur-xl opacity-50 animate-pulse" />
                      <CheckCircle className="h-8 w-8 text-green-500 relative z-10" />
                    </div>
                    <div>
                      <p className="font-semibold text-white text-lg">
                        Trial uploaded successfully!
                      </p>
                      <p className="text-sm text-green-400 font-mono mt-1">
                        Trial ID: <span className="text-white">{uploadResult.trial_id}</span>
                      </p>
                      {uploadResult.participant_count && (
                        <p className="text-sm text-gray-400 mt-1">
                          Participants: <span className="text-green-400">{uploadResult.participant_count}</span>
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button
                      onClick={async () => {
                        try {
                          const blob = await apiClient.downloadReport(uploadResult.trial_id)
                          const url = window.URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = `trial_report_${uploadResult.trial_id}.pdf`
                          document.body.appendChild(a)
                          a.click()
                          window.URL.revokeObjectURL(url)
                          document.body.removeChild(a)
                          toast({ title: 'Success', description: 'Report downloaded successfully' })
                        } catch (error: any) {
                          toast({ title: 'Error', description: 'Failed to download report', variant: 'destructive' })
                        }
                      }}
                      variant="outline"
                      className="flex-1 border-blue-500/50 text-blue-400 hover:bg-blue-950/30 hover:border-blue-400"
                    >
                      <File className="h-4 w-4 mr-2" />
                      Download Report
                    </Button>
                    <Button
                      onClick={handleValidateRules}
                      disabled={validating}
                      variant="outline"
                      className="flex-1 border-green-500/50 text-green-400 hover:bg-green-950/30 hover:border-green-400"
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      {validating ? 'Validating...' : 'Validate Rules'}
                    </Button>
                    <Button
                      onClick={() => router.push(`/ml-analysis?trial_id=${uploadResult.trial_id}`)}
                      className="flex-1 bg-green-600 hover:bg-green-500 text-white border-2 border-green-400 green-glow-hover"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Run ML Analysis
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Validation Results */}
          {validationResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6"
            >
              <Card className={`blockchain-block glass-effect ${
                validationResult.status === 'passed' 
                  ? 'border-green-500/50 bg-green-950/30' 
                  : 'border-green-500/50 bg-green-950/30'
              }`}>
                <CardHeader>
                  <CardTitle className="text-xl text-white flex items-center gap-2">
                    <Shield className="h-5 w-5 text-green-400" />
                    Validation Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className={`p-4 rounded-lg border ${
                      validationResult.status === 'passed' 
                        ? 'bg-green-500/10 border-green-500/30' 
                        : 'bg-green-500/10 border-green-500/30'
                    }`}>
                      <p className={`font-semibold text-lg ${
                        validationResult.status === 'passed' ? 'text-green-400' : 'text-green-500'
                      }`}>
                        Status: {validationResult.status.toUpperCase()}
                      </p>
                    </div>
                    {validationResult.rules_passed && validationResult.rules_passed.length > 0 && (
                      <div className="p-4 bg-green-950/20 rounded-lg border border-green-500/20">
                        <p className="text-sm font-semibold text-green-400 mb-2">Passed Rules:</p>
                        <ul className="text-sm text-white space-y-1">
                          {validationResult.rules_passed && Array.isArray(validationResult.rules_passed) ? validationResult.rules_passed.map((rule: string, idx: number) => (
                            <li key={idx} className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                              {rule}
                            </li>
                          )) : <li className="text-white/70 text-sm">No rules passed</li>}
                        </ul>
                      </div>
                    )}
                    {validationResult.rules_failed && validationResult.rules_failed.length > 0 && (
                      <div className="p-4 bg-green-950/30 rounded-lg border border-green-500/40">
                        <p className="text-sm font-semibold text-green-400 mb-2">Failed Rules:</p>
                        <ul className="text-sm text-white space-y-1">
                          {validationResult.rules_failed && Array.isArray(validationResult.rules_failed) ? validationResult.rules_failed.map((rule: string, idx: number) => (
                            <li key={idx} className="flex items-center gap-2">
                              <AlertCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                              {rule}
                            </li>
                          )) : <li className="text-white/70 text-sm">No rules failed</li>}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

