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
					component: () => import('@/views/admin/job orders/JobOrders.vue'),
				},
			],
		},
  ],
})

export default router
