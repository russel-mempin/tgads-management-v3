<script setup lang="ts">
import { DatePicker } from 'primevue';
import { ref } from 'vue'
import { ArrowUp } from '@lucide/vue';
import { Clock, Check } from '@lucide/vue';

const dateFilter = ref(new Date);
const services = [
	{ name: 'Digital Printing', count: 88 },
	{ name: 'Offset Printing', count: 61 },
	{ name: 'Large Format', count: 44 },
	{ name: 'Binding & Finishing', count: 29 },
	{ name: 'Promotional Items', count: 18 },
]

const max = Math.max(...services.map(s => s.count))
</script>
<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Dashboard</h1>
			<h2>Monitor your business performance at a glance. Filter by month and year to review sales, revenue,
				service demand, and operational trends.</h2>
		</div>
		<div>
			<p class="text-xs montserrat font-semibold text-gray-500 mb-1">VIEWING PERIOD</p>
			<DatePicker v-model="dateFilter" showIcon view="month" dateFormat="MM yy" size="small" />
		</div>
	</section>
	<section class="mt-4">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-1 h-6 bg-blue-600 rounded-r-full"></div>
			<p class="text-sm font-semibold montserrat text-slate-700">FINANCIAL</p>
			<p class="text-sm montserrat text-slate-600">4 metrics</p>
		</div>
		<div class="grid grid-cols-4 gap-4">
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Sales Today</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">₱99,999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						<ArrowUp class="size-3" />
						100.0%
					</span>
					<span class="text-xs text-slate-400">vs. yesterday</span>
				</div>
			</div>
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Sales This Month</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">₱99,999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						<ArrowUp class="size-3" />
						100.0%
					</span>
					<span class="text-xs text-slate-400">vs. last month</span>
				</div>
			</div>
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Gross Profit This Month</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">₱99,999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						<ArrowUp class="size-3" />
						100.0%
					</span>
					<span class="text-xs text-slate-400">31.3% margin</span>
				</div>
			</div>
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Outstanding Receiveables
				</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">₱99,999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						3 overdue
					</span>
					<span class="text-xs text-slate-400">14 open invoices</span>
				</div>
			</div>
		</div>
	</section>
	<section class="mt-4">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-1 h-6 bg-green-600 rounded-r-full"></div>
			<p class="text-sm font-semibold montserrat text-slate-700">SALES</p>
			<p class="text-sm montserrat text-slate-600">4 metrics</p>
		</div>
		<div class="grid grid-cols-5 gap-5">
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-green-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Orders Today</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						<ArrowUp class="size-3" />
						100.0
					</span>
					<span class="text-xs text-slate-400">vs. yesterday</span>
				</div>
			</div>
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-green-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Average Order Value</p>
				<p class="text-4xl font-bold tracking-tight text-slate-900 mb-2 tabular-nums">₱99,999</p>
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
						<ArrowUp class="size-3" />
						100.0%
					</span>
					<span class="text-xs text-slate-400">vs. yesterday</span>
				</div>
			</div>
			<div
				class="col-span-3 bg-white border border-slate-200 border-l-4 border-l-emerald-600 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Orders by Service</p>
				<div class="flex flex-col gap-3">
					<div v-for="service in services" :key="service.name" class="grid items-center gap-2.5"
						style="grid-template-columns: 140px 1fr 32px">
						<span class="text-xs text-slate-600 truncate">{{ service.name }}</span>
						<div class="h-2 bg-slate-100 rounded-full overflow-hidden">
							<div class="h-full bg-emerald-500 rounded-full opacity-75 transition-all duration-700"
								:style="{ width: `${(service.count / max) * 100}%` }" />
						</div>
						<span class="text-xs text-slate-400 text-right tabular-nums">{{ service.count }}</span>
					</div>
				</div>
			</div>
		</div>
	</section>
	<section class="mt-4">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-1 h-6 bg-orange-600 rounded-r-full"></div>
			<p class="text-sm font-semibold montserrat text-slate-700">PRODUCTION</p>
			<p class="text-sm montserrat text-slate-600">2 metrics</p>
		</div>
		<div class="grid grid-cols-2 gap-5">
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-amber-500 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Jobs Pending</p>
				<div class="flex items-center gap-4">
					<div class="w-11 h-11 rounded-xl bg-amber-50 flex items-center justify-center shrink-0">
						<Clock class="size-5 text-amber-500" />
					</div>
					<div>
						<p class="text-4xl font-bold tracking-tight text-amber-500 tabular-nums leading-none">47</p>
						<p class="text-xs text-slate-400 mt-1">12 due today</p>
					</div>
				</div>
			</div>
			<div
				class="bg-white border border-slate-200 border-l-4 border-l-amber-500 rounded-lg p-5 hover:shadow-md transition-shadow">
				<p class="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Jobs Completed Today</p>
				<div class="flex items-center gap-4">
					<div class="w-11 h-11 rounded-xl bg-green-50 flex items-center justify-center shrink-0">
						<Check class="size-5 text-green-500" />
					</div>
					<div>
						<p class="text-4xl font-bold tracking-tight text-green-500 tabular-nums leading-none">47</p>
						<p class="text-xs text-slate-400 mt-1">12 due today</p>
					</div>
				</div>
			</div>
		</div>
	</section>

</template>