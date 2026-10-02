import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('research_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.startsWith('/auth/')) {
      window.dispatchEvent(new Event('research:session-expired'))
    }
    return Promise.reject(error)
  },
)

export default api