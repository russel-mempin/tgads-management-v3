<script setup lang="ts">
import type { JobOrder } from '@/types/jobOrder';
import { getPaymentStatusColor, getJobStatusColor, formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	entityData: JobOrder
}>()
</script>

<template>
	<section class="border border-default bg-default p-4 rounded-md">
		<div class="flex justify-between border-b-3 border-dashed border-default pb-2">
			<div>
				<div class="flex items-center gap-2 mb-2">
					<p class="text-2xl font-semibold">Job Order #{{ entityData.jo_number }}</p>
					<UBadge :color="getPaymentStatusColor(entityData.payment_status)">{{ entityData.payment_status }}
					</UBadge>
					<UBadge :color="getJobStatusColor(entityData.overall_job_status)">{{ entityData.overall_job_status
						}}</UBadge>
				</div>
				<div class="flex gap-4 text-muted">
					<p>Received {{ formatDate(entityData.date_received) }}</p>
					<p>Updated by {{ entityData.updated_by_name }}, {{ formatDate(entityData.updated_at) }}</p>
					<p>Created by {{ entityData.created_by_name }}</p>
				</div>
			</div>
			<div class="text-end">
				<p class="font-semibold">{{ entityData.customer_name || 'Anonymous Customer' }}</p>
				<p class="text-muted">{{ entityData.customer_contact_no || 'Contact No. N/A' }}</p>
				<p class="text-muted">{{ entityData.customer_email || 'Email N/A' }}</p>
			</div>
		</div>
		<div class="mt-2 grid grid-cols-3 gap-4 divide-x-1 divide-default">
			<div class="py-2">
				<p class="uppercase text-sm text-muted">Total Due</p>
				<p class="text-xl font-semibold">{{ formatCurrency(entityData.total_due) }}</p>
			</div>
			<div class="py-2">
				<p class="uppercase text-sm text-muted">Total Paid</p>
				<p class="text-xl font-semibold">{{ formatCurrency(entityData.total_paid) }}</p>
			</div>
			<div class="py-2">
				<p class="uppercase text-sm text-muted">Balance</p>
				<p class="text-xl font-semibold">{{ formatCurrency(entityData.balance) }}</p>
			</div>
		</div>
	</section>
</template>