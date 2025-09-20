import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data)
    } else if (error.response?.status === 404) {
      console.error('Endpoint not found:', error.config.url)
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
