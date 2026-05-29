<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import NavbarItem from './NavbarItem.vue';
import { LayoutDashboard, BriefcaseBusiness, BanknoteArrowUp, BanknoteArrowDown, Landmark, BookUser, Sheet, ConciergeBell, UserCog, Activity, Layers, SunMoon,  LogOut } from '@lucide/vue';
import type { Component } from 'vue'

const authStore = useAuthStore()

type NavItem = {
	to: string
	label: string
	icon: Component
}

const adminItems: NavItem[] = [
	{ to: '/admin/dashboard', label: "Dashboard", icon: LayoutDashboard },
	{ to: '/admin/job-orders', label: "Job Orders", icon: BriefcaseBusiness },
	{ to: '/admin/sales', label: "Sales", icon: BanknoteArrowUp },
	{ to: '/admin/expenses', label: "Expenses", icon: BanknoteArrowDown },
	{ to: '/admin/deposits', label: "Deposits", icon: Landmark },
	{ to: '/admin/customers', label: "Customers", icon: BookUser },
	{ to: '/admin/cash-flow', label: "Cash Flow", icon: Sheet },
	{ to: '/admin/manage-services', label: "Manage Services", icon: ConciergeBell },
	{ to: '/admin/manage-extras', label: "Manage Extras", icon: Layers },
	{ to: '/admin/manage-users', label: "Manage Users", icon: UserCog },
	{ to: '/admin/audit-logs', label: "Audit Logs", icon: Activity }
]

const logout = () => {
	authStore.logout()
}

const toggleTheme = () => {
	console.log("Theme toggled")
}
</script>

<template>
	<nav class="h-screen w-[300px] flex flex-col justify-between transition-all duration-300 bg-transparent">
		<!-- Header -->
		<div class="mx-4 py-4">
			<div class="flex items-center">
				<span>
					<p class="text-xl text-slate-800 font-semibold montserrat">Team Graphics ADS</p>
					<p class="text-slate-800 montserrat">Management System</p>
				</span>
			</div>
		</div>
		<!-- Navigation -->
		<p class="ml-4 mb-2 montserrat font-semibold text-slate-600 text-sm">NAVIGATION</p>
		<div class="flex flex-col px-4 gap-2 inter">
			<NavbarItem v-for="link in adminItems" :key="link.to" :to="link.to" :label="link.label" :icon="link.icon" />
		</div>
		<!-- Footer / User -->
		<div class="mx-4 py-4 mt-auto flex items-center justify-between">
			<div class="flex items-center">
				<span class="ml-2">
					<p class="text-lg font-medium text-slate-800 inter">{{`${authStore.user?.first_name} ${authStore.user?.last_name}`}}</p>
				</span>
			</div>
			<div class="flex items-center">
				<button @click="toggleTheme"
					class="text-gray-500 p-1 hover:bg-blue-200 hover:text-gray-800 rounded-full">
					<SunMoon />
				</button>
				<button @click="logout"
					class="text-gray-500 p-1 hover:bg-blue-200 hover:text-gray-800 rounded-full">
					<LogOut />
				</button>
			</div>
		</div>
	</nav>
</template>