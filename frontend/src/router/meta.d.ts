import 'vue-router'
import type { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    breadcrumb?: string
    breadcrumbParent?: { label: string, to: string }
    subtitle?: string | ((auth: ReturnType<typeof useAuthStore>) => string)
  }
}