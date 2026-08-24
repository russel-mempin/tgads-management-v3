<script setup lang="ts">
import type { JobOrder } from '@/types/jobOrder';
import { getPaymentStatusColor, getJobStatusColor, formatCurrency, formatDate } from '@/utils/formatters';

const props = defineProps<{
	jobOrder: JobOrder
}>()
</script>

<template>
	<section class="flex items-center gap-6">
		<h1 class="text-2xl font-semibold text-highlighted">Job Order #{{ jobOrder.jo_number }}</h1>
		<div class="flex gap-2">
			<UBadge :color="getPaymentStatusColor(jobOrder.payment_status)" variant="subtle" size="lg"
				class="font-semibold">{{
					jobOrder.payment_status }}</UBadge>
			<UBadge :color="getJobStatusColor(jobOrder.overall_job_status)" variant="subtle" size="lg"
				class="font-semibold">{{
					jobOrder.overall_job_status }}</UBadge>
		</div>
	</section>
	<section class="grid grid-cols-3 gap-6">
		<div class="border border-default bg-default rounded-md p-4">
			<p class="text-sm text-muted uppercase font-semibold">Total Due</p>
			<p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_due) }}</p>
		</div>
		<div class="border border-default bg-default rounded-md p-4">
			<p class="text-sm text-muted uppercase font-semibold">Total Paid</p>
			<p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_paid) }}</p>
		</div>
		<div class="border border-default bg-default rounded-md p-4"
			:class="jobOrder.balance > 0 ? 'border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30' : 'border-default bg-default'">
			<p class="text-sm uppercase font-semibold"
				:class="jobOrder.balance > 0 ? 'text-red-700 dark:text-red-400' : 'text-muted'">Balance</p>
			<p class="text-2xl font-bold mt-1"
				:class="jobOrder.balance > 0 ? 'text-red-700 dark:text-red-400' : 'text-highlighted'">
				{{ formatCurrency(jobOrder.balance) }}
			</p>
		</div>
	</section>
	<section class="bg-default border border-default rounded-md">
		<div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
			<div class="flex items-center gap-2">
				<UIcon name="i-lucide-user" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<h2 class="text-highlighted font-semibold">Customer and Order Info</h2>
			</div>
		</div>
		<div class="m-6 grid grid-cols-3 gap-6">
			<div>
				<p class="text-sm text-muted uppercase">Name</p>
				<p class="text-base text-highlighted">{{ jobOrder.customer_name ?? 'Walk-in' }}</p>
			</div>
			<div>
				<p class="text-sm text-muted uppercase">Contact No.</p>
				<p class="text-base text-highlighted">{{ jobOrder.customer_contact_no ?? '—' }}</p>
			</div>
			<div>
				<p class="text-sm text-muted uppercase">Email</p>
				<p class="text-base text-highlighted">{{ jobOrder.customer_email ?? '—' }}</p>
			</div>
			<div>
				<p class="text-sm text-muted uppercase">Date Received</p>
				<p class="text-base text-highlighted">{{ formatDate(jobOrder.date_received) }}</p>
			</div>
			<div>
				<p class="text-sm text-muted uppercase">Last Updated</p>
				<p class="text-base text-highlighted">{{ formatDate(jobOrder.updated_at) }}</p>
			</div>
			<div>
				<p class="text-sm text-muted uppercase">Last Update By</p>
				<p class="text-base text-highlighted">{{ jobOrder.updated_by_name }}</p>
			</div>
		</div>
	</section>
</template>