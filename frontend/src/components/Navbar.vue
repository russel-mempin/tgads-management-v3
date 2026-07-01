<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import NavbarItem from './NavbarItem.vue';
import { LayoutDashboard, BriefcaseBusiness, BanknoteArrowUp, BanknoteArrowDown, Landmark, BookUser, Sheet, ConciergeBell, UserCog, Activity, Layers, LogOut } from '@lucide/vue';
import type { Component } from 'vue'
import { computed } from 'vue'

const authStore = useAuthStore()

type NavItem = {
	to: string
	label: string
	icon: Component
	category: string
	adminOnly?: boolean
	ownerOnly?: boolean
	superuserOnly?: boolean
}

const allItems: NavItem[] = [
	{ to: '/dashboard', label: "Dashboard", icon: LayoutDashboard, category: 'None' },
	// Operations - all roles
	{ to: '/job-orders', label: "Job Orders", icon: BriefcaseBusiness, category: 'Operations' },
	{ to: '/customers', label: "Customers", icon: BookUser, category: 'Operations' },
	// Finance - all roles
	{ to: '/sales', label: authStore.isOwner ? "Sales" : "Daily Sales", icon: BanknoteArrowUp, category: 'Finance' },
	{ to: '/expenses', label: authStore.isOwner ? "Expenses" : "Daily Expenses", icon: BanknoteArrowDown, category: 'Finance' },
	// Finance - admin and above
	{ to: '/deposits', label: "Deposits", icon: Landmark, category: 'Finance', adminOnly: true },
	// Reports - owner and above
	{ to: '/reports/daily', label: "Daily Collection", icon: Sheet, category: 'Reports', ownerOnly: true },
	{ to: '/reports/monthly', label: "Monthly Performance", icon: Sheet, category: 'Reports', ownerOnly: true },
	// Settings - admin and above
	{ to: '/manage-services', label: "Manage Services", icon: ConciergeBell, category: 'Settings', adminOnly: true },
	{ to: '/manage-extras', label: "Manage Extras", icon: Layers, category: 'Settings', adminOnly: true },
	{ to: '/manage-users', label: "Manage Users", icon: UserCog, category: 'Settings', adminOnly: true },
	// Settings - superuser only
	{ to: '/audit-logs', label: "Audit Logs", icon: Activity, category: 'Settings', superuserOnly: true },
]

const visibleItems = computed(() => allItems.filter(item => {
	if (item.superuserOnly) return authStore.isSuperuser
	if (item.ownerOnly) return authStore.isOwner
	if (item.adminOnly) return authStore.isAdmin
	return true
}))

const navigationItems = computed(() => visibleItems.value.filter(link => link.category === 'None'))
const operationItems = computed(() => visibleItems.value.filter(link => link.category === 'Operations'))
const financeItems = computed(() => visibleItems.value.filter(link => link.category === 'Finance'))
const reportItems = computed(() => visibleItems.value.filter(link => link.category === 'Reports'))
const settingItems = computed(() => visibleItems.value.filter(link => link.category === 'Settings'))

const logout = () => {
	authStore.logout()
}

const toggleTheme = () => {
	console.log("Theme toggled")
}
</script>

<template>
	<nav
		class="bg-white border-r border-slate-200 h-screen w-[300px] flex flex-col justify-between transition-all duration-300">
		<!-- Header -->
		<div class="mx-4 py-4">
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-md bg-blue-200 font-bold text-slate-700">TG</div>
				<span>
					<p class="text-lg text-slate-800 font-semibold montserrat">Team Graphics ADS</p>
					<p class="text-sm text-slate-800 tracking-wider montserrat">Management System</p>
				</span>
			</div>
		</div>

		<!-- Navigation -->
		<div class="flex flex-col px-4 inter">
			<NavbarItem v-for="link in navigationItems" :key="link.to" :to="link.to" :label="link.label"
				:icon="link.icon" />
		</div>

		<template v-if="operationItems.length">
			<p class="ml-8 my-2 tracking-wider montserrat font-semibold text-slate-600 text-sm">OPERATIONS</p>
			<div class="flex flex-col gap-[0.2rem] px-4 inter">
				<NavbarItem v-for="link in operationItems" :key="link.to" :to="link.to" :label="link.label"
					:icon="link.icon" />
			</div>
		</template>

		<template v-if="reportItems.length">
			<p class="ml-8 my-2 tracking-wider montserrat font-semibold text-slate-600 text-sm">REPORTS</p>
			<div class="flex flex-col gap-[0.2rem] px-4 inter">
				<NavbarItem v-for="link in reportItems" :key="link.to" :to="link.to" :label="link.label"
					:icon="link.icon" />
			</div>
		</template>

		<template v-if="financeItems.length">
			<p class="ml-8 my-2 tracking-wider montserrat font-semibold text-slate-600 text-sm">FINANCE</p>
			<div class="flex flex-col gap-[0.2rem] px-4 inter">
				<NavbarItem v-for="link in financeItems" :key="link.to" :to="link.to" :label="link.label"
					:icon="link.icon" />
			</div>
		</template>

		<template v-if="settingItems.length">
			<p class="ml-8 my-2 tracking-wider montserrat font-semibold text-slate-600 text-sm">SETTINGS</p>
			<div class="flex flex-col gap-[0.2rem] px-4 inter">
				<NavbarItem v-for="link in settingItems" :key="link.to" :to="link.to" :label="link.label"
					:icon="link.icon" />
			</div>
		</template>

		<!-- Footer / User -->
		<div class="mx-4 py-4 mt-auto flex items-center justify-between border-t border-slate-200">
			<div class="flex items-center">
				<div class="p-2 rounded-full bg-blue-200">
					{{ `${authStore.user?.first_name[0]}${authStore.user?.last_name[0]}` }}
				</div>
				<span class="ml-2">
					<p class="text-lg font-medium text-slate-800 inter">
						{{ `Hi, ${authStore.user?.first_name}!` }}
					</p>
				</span>
			</div>
			<button @click="authStore.logout"
				class="text-gray-500 p-1 hover:bg-blue-200 hover:text-gray-800 rounded-full">
				<LogOut />
			</button>
		</div>
	</nav>
</template>

<style>
.avatar {
	width: 28px;
	height: 28px;
	border-radius: 50%;
	background: #E7EAFB;
	color: var(--primary);
}
</style>