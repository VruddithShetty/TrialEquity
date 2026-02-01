import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests (skip for login/registration endpoints)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  // Only add token if it exists AND we're not logging in
  const isLoginRequest = config.url?.includes('/api/login') || config.url?.includes('/api/register')
  
  if (token && !isLoginRequest) {
    // Ensure Authorization header is always set, even for multipart requests
    if (!config.headers) {
      config.headers = {} as any
    }
    if (typeof config.headers === 'object' && !Array.isArray(config.headers)) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  
  // For FormData, don't set Content-Type (let browser set it with boundary)
  if (config.data instanceof FormData && config.headers) {
    delete config.headers['Content-Type']
  }
  
  return config
})

export interface TrialUploadResponse {
  trial_id: string
  filename: string
  status: string
  participant_count?: number
  message?: string
}

export interface MLBiasCheckResponse {
  trial_id: string
  decision: 'ACCEPT' | 'REVIEW' | 'REJECT'
  fairness_score: number
  metrics: {
    outlier_score: number
    is_outlier: boolean
    bias_probability: number
    fairness_metrics: {
      demographic_parity: number
      disparate_impact_ratio: number
      equality_of_opportunity: number
    }
    statistical_tests: {
      chi2_gender: number
      p_value_gender: number
      chi2_ethnicity: number
      p_value_ethnicity: number
    }
  }
  explanations?: any
  recommendations?: string[]
  rejection_summary?: string  // Clear explanation if rejected
}

export interface BlockchainWriteResponse {
  trial_id: string
  tx_hash: string
  block_number?: number
  timestamp: string
  status: string
}

export interface BlockchainVerifyResponse {
  trial_id: string
  is_valid: boolean
  hash_match: boolean
  tamper_detected: boolean
  verification_timestamp: string
}

export const apiClient = {
  uploadTrial: async (file: File): Promise<TrialUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    
    // Get token to ensure it's available
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('No authentication token found. Please login first.')
    }
    
    // For multipart/form-data, axios will handle Content-Type automatically
    // The interceptor will add Authorization header and remove Content-Type for FormData
    const response = await api.post('/api/uploadTrial', formData)
    return response.data
  },

  validateRules: async (trialId: string) => {
    const response = await api.post('/api/validateRules', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  runMLBiasCheck: async (trialId: string): Promise<MLBiasCheckResponse> => {
    const response = await api.post('/api/runMLBiasCheck', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  writeToBlockchain: async (trialId: string): Promise<BlockchainWriteResponse> => {
    const response = await api.post('/api/blockchain/write', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  verifyBlockchain: async (trialId: string): Promise<BlockchainVerifyResponse> => {
    const response = await api.post('/api/blockchain/verify', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  getAuditLogs: async (trialId?: string) => {
    const response = await api.get('/api/admin/audit/logs', {
      params: { trial_id: trialId },
    })
    return response.data
  },

  explainModel: async (trialId: string) => {
    const response = await api.post('/api/model/explain', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  downloadReport: async (trialId: string) => {
    const response = await api.get('/api/downloadReport', {
      params: { trial_id: trialId },
      responseType: 'blob',
    })
    return response.data
  },

  downloadBlockchainSummary: async () => {
    const response = await api.get('/api/blockchain/summary-report', {
      responseType: 'blob',
    })
    return response.data
  },

  compareBlockchains: async () => {
    const response = await api.get('/api/blockchain/compare')
    return response.data
  },

  getAllTrials: async () => {
    const response = await api.get('/api/trials')
    return response.data
  },

  getLatestTrial: async () => {
    try {
      const trials = await apiClient.getAllTrials()
      if (trials && trials.length > 0) {
        // Sort by creation date (assuming trials have a created_at or we can use trial_id order)
        // Return the first one (most recent if sorted by timestamp desc)
        return trials[0]
      }
      return null
    } catch (error: any) {
      console.error('Failed to get latest trial:', error)
      return null
    }
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/login', {
      email,
      password
    })
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    return response.data
  },

  logout: async () => {
    try {
      // Clear local storage
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    } catch (_) {
      // noop
    }
  },

  createUser: async (userData: {
    email: string
    username: string
    password: string
    role: string
    organization?: string
  }) => {
    const response = await api.post('/api/admin/users', userData)
    return response.data
  },

  // Digital Signatures
  signTrial: async (trialId: string) => {
    const response = await api.post('/api/trial/sign', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  verifySignature: async (trialId: string) => {
    const response = await api.post('/api/trial/verify-signature', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  // IPFS
  uploadToIPFS: async (trialId: string) => {
    const response = await api.post('/api/ipfs/upload', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  // Tokenization
  tokenizeTrial: async (trialId: string) => {
    const response = await api.post('/api/trial/tokenize', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  // Zero-Knowledge Proofs
  generateZKP: async (trialId: string) => {
    const response = await api.post('/api/zkp/generate', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  verifyZKP: async (trialId: string) => {
    const response = await api.post('/api/zkp/verify', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  // Admin
  getNodes: async () => {
    const response = await api.get('/api/admin/nodes')
    return response.data
  },

  getUsers: async () => {
    const response = await api.get('/api/admin/users')
    return response.data
  },

  retrainModel: async () => {
    const response = await api.post('/api/admin/retrain-model')
    return response.data
  },

  // Alerts
  triggerTamperAlert: async (trialId: string) => {
    const response = await api.post('/api/alerts/tamper', null, {
      params: { trial_id: trialId },
    })
    return response.data
  },

  // Delete Trial
  deleteTrial: async (trialId: string) => {
    const response = await api.delete(`/api/trials/${trialId}`)
    return response.data
  },

  // Get CSV data for trial
  getTrialCsvData: async (trialId: string) => {
    const response = await api.get(`/api/trials/${trialId}/csv`)
    return response.data
  },
}

