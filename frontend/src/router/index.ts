import { createRouter, createWebHistory } from 'vue-router'

const DEFAULT_TITLE = 'TGADS Management System';

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    adminOnly?: boolean
    ownerOnly?: boolean
    superuserOnly?: boolean
  }
}

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
      path: '/job-orders/print/:job_order_id',
      component: () => import('@/views/job_orders/PrintJobOrder.vue'),
      meta: { requiresAuth: true, title: `Print Job Order` },
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
            title: 'Dashboard',
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
            title: 'Job Orders',
            breadcrumb: 'Job Orders',
            subtitle: 'View and manage all job orders. Use filters to quickly find the ones you need.'
          }
        },
        {
          path: 'job-orders/view/:job_order_id',
          component: () => import('@/views/job_orders/ViewJobOrder.vue'),
          meta: {
            title: 'Job Orders - View',
            breadcrumb: 'View Job Order',
            breadcrumbParent: { label: 'Job Orders', to: '/job-orders' },
            subtitle: 'See full information about a Job Order.'
          }
        },
        {
          path: 'job-orders/add',
          component: () => import('@/views/job_orders/AddJobOrder.vue'),
          meta: {
            title: 'Job Orders - Add',
            breadcrumb: 'Add Job Order',
            breadcrumbParent: { label: 'Job Orders', to: '/job-orders' },
            subtitle: 'Create a new Job Order upon clicking save.'
          }
        },
        {
          path: 'review-data',
          component: () => import('@/views/NeedsReview.vue'),
          meta: {
            title: 'Needs Review',
            breadcrumb: 'Needs Review',
            breadcrumbParent: { label: 'Needs Review', to: 'review-data' },
            subtitle: 'See data that needs your attention.'
          }
        },
        {
          path: 'review-data/job-orders/:entity_id',
          component: () => import('@/views/needs_review/ReviewJob.vue'),
          name: 'review-job-order',
          meta: {
            title: 'Needs Review - Job Order',
            breadcrumb: 'Needs Review - Job Order',
            breadcrumbParent: { label: 'Needs Review', to: 'review-data' },
            subtitle: 'View full information about the job that is for review and resolve it.'
          }
        },
        {
          path: 'review-data/job-items/:entity_id',
          component: () => import('@/views/needs_review/ReviewJob.vue'),
          name: 'review-job-item',
          meta: {
            title: 'Needs Review - Job Item',
            breadcrumb: 'Needs Review - Job Item',
            breadcrumbParent: { label: 'Needs Review', to: 'review-data' },
            subtitle: 'View full information about the job that is for review and resolve it.'
          }
        },
        {
          path: 'review-data/payments/:entity_id',
          component: () => import('@/views/needs_review/ReviewPayment.vue'),
          meta: {
            title: 'Needs Review - Payment',
            breadcrumb: 'Needs Review - Payment',
            breadcrumbParent: { label: 'Needs Review', to: 'review-data' },
            subtitle: 'View full information about the payment that is for review and resolve it.'
          }
        },
        {
          path: 'voided-jobs',
          component: () => import('@/views/VoidedJobs.vue'),
          meta: {
            title: 'Voided Jobs',
            breadcrumb: 'Voided Jobs',
            breadcrumbParent: { label: 'Voided Jobs', to: 'voided-jobs' },
            subtitle: 'View and verify job orders that have been voided to ensure all JO numbers are accounted for.'
          }
        },
        {
          path: 'misc-sales',
          component: () => import('@/views/MiscSales.vue'),
          meta: {
            title: 'Misc Sales',
            breadcrumb: 'Misc Sales',
            breadcrumbParent: { label: 'Misc Sales', to: 'misc-sales' },
            subtitle: 'View and record payments for miscellaneous sales without job orders.'
          }
        },
        {
          path: 'expenses',
          component: () => import('@/views/Expenses.vue'),
          meta: {
            title: 'Expenses',
            breadcrumb: 'Expenses',
            breadcrumbParent: { label: 'Expenses', to: 'expenses' },
            subtitle: 'View and record expense data.'
          }
        },
      ]
    }
  ],
})

router.beforeEach((to) => {
  // Set title from meta, fallback to default
  document.title = to.meta.title || DEFAULT_TITLE;
});

export default router
