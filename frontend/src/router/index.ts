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
					path: 'job-orders',
					component: () => import('@/views/admin/job_orders/JobOrders.vue'),
				},
				{
					path: 'job-orders/add',
					component: () => import('@/views/admin/job_orders/AddJobOrder.vue'),
				},
			],
		},
  ],
})

export default router
