import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
			path: '/admin',
			component: () => import('@/layouts/AdminLayout.vue'),
			meta: { requiresAdmin: true },
			children: [
				{
					path: 'dashboard',
					component: () => import('@/views/admin/Dashboard.vue'),
				},
				{
					path: 'job-orders',
					component: () => import('@/views/admin/job_orders/JobOrders.vue'),
				},
				{
					path: 'job-orders/add',
					component: () => import('@/views/admin/job_orders/AddJobOrder.vue'),
				},
				{
					path: 'sales',
					component: () => import('@/views/admin/Sales.vue'),
				},
				{
					path: 'expenses',
					component: () => import('@/views/admin/Expenses.vue'),
				},
				{
					path: 'deposits',
					component: () => import('@/views/admin/Deposits.vue'),
				},
				{
					path: 'customers',
					component: () => import('@/views/admin/Customers.vue'),
				},
				{
					path: 'cash-flow',
					component: () => import('@/views/admin/CashFlow.vue'),
				},
				{
					path: 'manage-services',
					component: () => import('@/views/admin/ManageServices.vue'),
				},
				{
					path: 'manage-users',
					component: () => import('@/views/admin/ManageUsers.vue'),
				},
				{
					path: 'audit-logs',
					component: () => import('@/views/admin/AuditLogs.vue'),
				},
			],
		},
  ],
})

export default router
