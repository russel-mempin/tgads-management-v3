import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: 'http://127.0.0.1:8000'
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  const token = auth.user?.token

  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }

  return config
})

export default http
