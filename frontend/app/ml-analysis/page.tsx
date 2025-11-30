'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertTriangle, Brain, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient, MLBiasCheckResponse } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const COLORS = ['#10b981', '#22c55e', '#16a34a', '#15803d']

export default function MLAnalysisPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const trialId = searchParams.get('trial_id')
  const [loading, setLoading] = useState(false)
  const [explaining, setExplaining] = useState(false)
  const [biasResult, setBiasResult] = useState<MLBiasCheckResponse | null>(null)
  const [explanation, setExplanation] = useState<any>(null)
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
            
            // Backend is ready, try login
            const result = await apiClient.login('test@example.com', 'test123')
            if (result.access_token) {
              setAuthenticated(true)
              console.log('✅ Auto-login successful')
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
    if (trialId && authenticated) {
      runBiasCheck()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trialId, authenticated])

  const runBiasCheck = async () => {
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

    setLoading(true)
    try {
      const result = await apiClient.runMLBiasCheck(trialId)
      setBiasResult(result)
    } catch (error: any) {
      console.error('Bias check error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to run bias analysis'
      console.error('Error details:', error.response?.data)
      
      // If it's an auth error, try to re-login
      if (error.response?.status === 401) {
        try {
          await apiClient.login('test@example.com', 'test123')
          setAuthenticated(true)
          // Retry the bias check
          setTimeout(() => runBiasCheck(), 1000)
          return
        } catch (loginError) {
          toast({
            title: 'Authentication Failed',
            description: 'Please refresh the page to login again.',
            variant: 'destructive',
          })
        }
      } else {
        toast({
          title: 'Analysis Failed',
          description: errorMessage,
          variant: 'destructive',
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleExplainModel = async () => {
    if (!trialId) return

    setExplaining(true)
    try {
      const result = await apiClient.explainModel(trialId)
      setExplanation(result)
      toast({
        title: 'Model Explanation',
        description: 'SHAP/LIME explanations generated',
      })
    } catch (error: any) {
      toast({
        title: 'Explanation Failed',
        description: error.response?.data?.detail || 'Failed to generate explanation',
        variant: 'destructive',
      })
    } finally {
      setExplaining(false)
    }
  }

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'ACCEPT':
        return <CheckCircle className="h-8 w-8 text-green-600" />
      case 'REVIEW':
        return <AlertTriangle className="h-8 w-8 text-green-500" />
      case 'REJECT':
        return <XCircle className="h-8 w-8 text-green-700" />
      default:
        return null
    }
  }

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'ACCEPT':
        return 'bg-green-950/30 border-green-500 text-white'
      case 'REVIEW':
        return 'bg-green-950/40 border-green-600 text-white'
      case 'REJECT':
        return 'bg-green-950/50 border-green-700 text-white'
      default:
        return 'bg-green-950/20 border-green-500/30 text-white'
    }
  }

  if (!trialId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-white">No trial ID provided</p>
      </div>
    )
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
              <h1 className="text-4xl font-bold text-white mb-2">ML Bias Analysis</h1>
              <p className="text-white/70">Trial ID: {trialId}</p>
            </div>
            <div className="flex gap-2">
              <Button onClick={runBiasCheck} disabled={loading}>
                {loading ? 'Analyzing...' : 'Re-run Analysis'}
              </Button>
              {biasResult && (
                <Button
                  variant="outline"
                  onClick={handleExplainModel}
                  disabled={explaining}
                >
                  {explaining ? 'Explaining...' : 'Explain Model'}
                </Button>
              )}
            </div>
          </div>

          {loading && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center py-12">
                  <Brain className="h-12 w-12 text-green-400 animate-pulse" />
                  <p className="ml-4 text-white">Running ML bias detection...</p>
                </div>
              </CardContent>
            </Card>
          )}

          {biasResult && (
            <>
              {/* Decision Card */}
              <Card className={`mb-6 border-2 ${getDecisionColor(biasResult.decision)}`}>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    {getDecisionIcon(biasResult.decision)}
                    <div className="flex-1">
                      <h2 className="text-2xl font-bold mb-2">
                        Decision: {biasResult.decision}
                      </h2>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-5 w-5" />
                          <span className="font-semibold">
                            Fairness Score: {(biasResult.fairness_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Rejection Summary - Prominently displayed */}
                  {biasResult.decision === 'REJECT' && biasResult.rejection_summary && (
                    <div className="mt-6 p-4 bg-green-950/40 border border-green-600/40 rounded-lg">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="h-6 w-6 text-green-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white mb-2">Why Was This Trial Rejected?</h3>
                          <div className="text-sm text-white/80 whitespace-pre-line leading-relaxed">
                            {biasResult.rejection_summary}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Review Summary */}
                  {biasResult.decision === 'REVIEW' && (
                    <div className="mt-6 p-4 bg-green-950/30 border border-green-500/40 rounded-lg">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="h-6 w-6 text-green-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white mb-2">Review Required</h3>
                          <p className="text-sm text-white/80">
                            This trial has some concerns that require manual review by a regulator. 
                            Please check the recommendations below and review the fairness metrics.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-6 mb-6">
                {/* Fairness Metrics */}
                <Card>
                  <CardHeader>
                    <CardTitle>Fairness Metrics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-white">Demographic Parity</span>
                          <span className="text-sm font-semibold">
                            {(biasResult.metrics.fairness_metrics.demographic_parity * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-green-950/40 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{
                              width: `${biasResult.metrics.fairness_metrics.demographic_parity * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-white">Disparate Impact Ratio</span>
                          <span className="text-sm font-semibold">
                            {(biasResult.metrics.fairness_metrics.disparate_impact_ratio * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-green-950/40 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{
                              width: `${biasResult.metrics.fairness_metrics.disparate_impact_ratio * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-white">Equality of Opportunity</span>
                          <span className="text-sm font-semibold">
                            {(biasResult.metrics.fairness_metrics.equality_of_opportunity * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-green-950/40 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{
                              width: `${biasResult.metrics.fairness_metrics.equality_of_opportunity * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Statistical Tests */}
                <Card>
                  <CardHeader>
                    <CardTitle>Statistical Tests</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="p-4 bg-green-950/30 border border-green-500/20 rounded-lg">
                        <p className="text-sm font-semibold mb-2">Gender Distribution (Chi-square)</p>
                        <p className="text-xs text-white">
                          χ² = {biasResult.metrics.statistical_tests.chi2_gender.toFixed(4)}
                        </p>
                        <p className="text-xs text-white">
                          p-value = {biasResult.metrics.statistical_tests.p_value_gender.toFixed(4)}
                        </p>
                      </div>
                      <div className="p-4 bg-green-950/30 border border-green-500/20 rounded-lg">
                        <p className="text-sm font-semibold mb-2">Ethnicity Distribution (Chi-square)</p>
                        <p className="text-xs text-white">
                          χ² = {biasResult.metrics.statistical_tests.chi2_ethnicity.toFixed(4)}
                        </p>
                        <p className="text-xs text-white">
                          p-value = {biasResult.metrics.statistical_tests.p_value_ethnicity.toFixed(4)}
                        </p>
                      </div>
                      <div className="p-4 bg-green-950/30 border border-green-500/20 rounded-lg">
                        <p className="text-sm font-semibold mb-2">Outlier Detection</p>
                        <p className="text-xs text-white">
                          Score: {biasResult.metrics.outlier_score.toFixed(4)}
                        </p>
                        <p className="text-xs text-white">
                          Is Outlier: {biasResult.metrics.is_outlier ? 'Yes' : 'No'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recommendations */}
              {biasResult.recommendations && biasResult.recommendations.length > 0 && (
                <Card className="mb-6">
                  <CardHeader>
                    <CardTitle>Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {biasResult.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-blue-600 mt-1">•</span>
                          <span className="text-white">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Model Explanation */}
              {explanation && (
                <Card className="mb-6">
                  <CardHeader>
                    <CardTitle>Model Explanation (SHAP/LIME)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {explanation.shap_values && (
                        <div>
                          <h4 className="font-semibold mb-2">SHAP Values</h4>
                          <pre className="text-xs bg-green-950/40 text-white p-2 rounded overflow-auto max-h-40 border border-green-500/20">
                            {JSON.stringify(explanation.shap_values, null, 2)}
                          </pre>
                        </div>
                      )}
                      {explanation.lime_explanation && (
                        <div>
                          <h4 className="font-semibold mb-2">LIME Explanation</h4>
                          <div className="text-sm text-white">
                            {typeof explanation.lime_explanation === 'string' ? (
                              <p>{explanation.lime_explanation}</p>
                            ) : typeof explanation.lime_explanation === 'object' ? (
                              <div className="space-y-2">
                                {explanation.lime_explanation.explanation && (
                                  <p>{explanation.lime_explanation.explanation}</p>
                                )}
                                {explanation?.lime_explanation?.score !== undefined && (
                                  <p className="text-xs">Score: {explanation.lime_explanation.score}</p>
                                )}
                                {!explanation.lime_explanation.explanation && (
                                  <pre className="text-xs bg-green-950/40 text-white p-2 rounded overflow-auto border border-green-500/20">
                                    {explanation?.lime_explanation ? JSON.stringify(explanation.lime_explanation, null, 2) : 'No LIME explanation available'}
                                  </pre>
                                )}
                              </div>
                            ) : (
                              <pre className="text-xs bg-green-950/40 text-white p-2 rounded overflow-auto border border-green-500/20">
                                {JSON.stringify(explanation.lime_explanation, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      )}
                      {explanation.feature_importance && (
                        <div>
                          <h4 className="font-semibold mb-2">Feature Importance</h4>
                          <ul className="space-y-1">
                            {Object.entries(explanation.feature_importance).map(([key, value]: [string, any]) => (
                              <li key={key} className="flex justify-between text-sm">
                                <span>{key}</span>
                                <span className="font-semibold">{(value * 100).toFixed(2)}%</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4">
                {biasResult.decision !== 'REJECT' && (
                  <Button
                    onClick={() => router.push(`/blockchain?trial_id=${trialId}`)}
                    size="lg"
                    className="flex-1"
                  >
                    Write to Blockchain
                  </Button>
                )}
                <Button
                  onClick={() => router.push(`/regulator?trial_id=${trialId}`)}
                  variant="outline"
                  size="lg"
                >
                  View Audit Logs
                </Button>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
}

