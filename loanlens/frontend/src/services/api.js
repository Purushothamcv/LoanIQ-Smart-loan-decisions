import axios from 'axios'
import { API_BASE_URL, IS_DEVELOPMENT } from '../config/constants'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Set to false to avoid CORS issues
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    if (IS_DEVELOPMENT) {
      console.log('API Request:', config.method?.toUpperCase(), config.url)
      console.log('Request data:', config.data)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    if (IS_DEVELOPMENT) {
      console.log('API Response:', response.status, response.config.url)
    }
    return response
  },
  (error) => {
    console.error('API Error:', error)
    if (error.code === 'ERR_NETWORK') {
      console.error(`Network error - check if backend is running on ${API_BASE_URL}`)
    }
    return Promise.reject(error)
  }
)

export const loanApi = {
  // Predict loan status
  predictLoan: async (loanData) => {
    const response = await api.post('/predict', loanData)
    return response.data
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health')
    return response.data
  },

  // Get API info
  getApiInfo: async () => {
    const response = await api.get('/')
    return response.data
  }
}

export default api
