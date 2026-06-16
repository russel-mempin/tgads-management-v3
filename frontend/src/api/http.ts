import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: '/api',
  withCredentials: true
})

http.interceptors.request.use((config) => {
  console.log('INTERCEPTOR HIT:', config.baseURL, config.url)
  const auth = useAuthStore()
  const token = auth.user?.token

  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }

  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
    }
    return Promise.reject(error)
  },
)

export default http
