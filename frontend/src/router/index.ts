import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: '',
          component: () => import('@/views/LoginView.vue'),
        },
      ],
    },
    {
      path: '/job-orders/print/:jo_number',
      component: () => import('@/views/job_orders/PrintJobOrder.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'job-orders',
          component: () => import('@/views/job_orders/JobOrders.vue'),
        },
        {
          path: 'job-orders/add',
          component: () => import('@/views/job_orders/AddJobOrder.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'job-orders/view/:jo_number',
          component: () => import('@/views/job_orders/ViewJobOrder.vue'),
        },
        {
          path: 'job-orders/edit/:jo_number',
          component: () => import('@/views/job_orders/EditJobOrder.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'sales',
          component: () => import('@/views/Sales.vue'),
        },
        {
          path: 'expenses',
          component: () => import('@/views/Expenses.vue'),
        },
        {
          path: 'customers',
          component: () => import('@/views/Customers.vue'),
        },
        {
          path: 'deposits',
          component: () => import('@/views/Deposits.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'manage-services',
          component: () => import('@/views/ManageServices.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'manage-extras',
          component: () => import('@/views/ManageExtras.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'manage-users',
          component: () => import('@/views/ManageUsers.vue'),
          meta: { adminOnly: true },
        },
        {
          path: 'cash-flow',
          component: () => import('@/views/CashFlow.vue'),
          meta: { ownerOnly: true },
        },
        {
          path: 'audit-logs',
          component: () => import('@/views/AuditLogs.vue'),
          meta: { superuserOnly: true },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/'
  if (to.meta.adminOnly && !auth.isAdmin) return '/job-orders'
  if (to.meta.ownerOnly && !auth.isOwner) return '/job-orders'
  if (to.meta.superuserOnly && !auth.isSuperuser) return '/job-orders'
})

export default router
