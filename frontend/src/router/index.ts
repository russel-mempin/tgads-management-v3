import { createRouter, createWebHistory } from 'vue-router'

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
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: {
            breadcrumb: 'Dashboard',
            subtitle: (auth) => auth.isOwner
              ? 'See your business performance, workloads, and trends in one place.'
              : `View today's job orders and keep track of overdue items.`
          }
        },
        {
          path: 'job-orders',
          component: () => import('@/views/job_orders/JobOrders.vue'),
          meta: {
            breadcrumb: 'Job Orders',
            subtitle: 'View and manage all job orders. Use filters to quickly find the ones you need.'
          }
        },
        {
          path: 'job-orders/view/:jo_number',
          component: () => import('@/views/job_orders/ViewJobOrder.vue'),
          meta: {
            breadcrumb: 'View Job Order',
            breadcrumbParent: { label: 'Job Orders', to: '/job-orders' },
            subtitle: 'See full information about a Job Order.'
          }
        },
      ]
    }
  ],
})

export default router
