<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { JobOrder, Payment, ClaimingHistory, JobItemFromDB } from '@/types/job_orders';
import { getJobOrder } from '@/api/job_orders';
import { Button, Tag, useConfirm, ConfirmDialog, useToast } from 'primevue';
import { Trash, PenBox, Mail, Phone } from '@lucide/vue';
import { formatDate, formatCurrency } from '@/utils/formatters';
import JobItemsList from '@/components/JobItemsList.vue';
import PaymentsTable from '@/components/PaymentsTable.vue';
import ClaimsTable from '@/components/ClaimsTable.vue';
import HeaderTitle from '@/components/HeaderTitle.vue';
import { Info } from '@lucide/vue';
import { archiveJobOrder } from '@/api/job_orders';

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();
const toast = useToast();
const jobOrder = ref<JobOrder>();
onMounted(async () => {
	jobOrder.value = await getJobOrder(Number(route.params.jo_number))
});

const confirmDelete = (jo_number: number) => {
	confirm.require({
		message: 'Do you want to delete this job order?',
		header: 'Danger Zone',
		rejectLabel: 'Cancel',
		rejectProps: {
			label: 'Cancel',
			severity: 'secondary',
			outlined: true
		},
		acceptProps: {
			label: 'Delete',
			severity: 'danger'
		},
		accept: async () => {
			await archiveJobOrder(jo_number)
			toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Job order deleted', life: 3000 });
			router.push('/admin/job-orders')
		},
		reject: () => {
			toast.add({ severity: 'error', summary: 'Cancelled', detail: 'You have cancelled', life: 3000 });
		}
	});
}
</script>

<template>
	<ConfirmDialog>
		<template #icon>
			<Info class="w-10 h-10 text-red-500" />
		</template>
	</ConfirmDialog>
	<div class="mx-12 my-6">
		<section class="flex justify-between items-center">
			<HeaderTitle 
				title="View Job Order"
				subtitle="See full information about a Job Order."
			/>
			<div class="flex gap-6">
				<Button @click="router.push(`/admin/job-orders/edit/${route.params.jo_number}`)" severity="warn"
					class="w-26" label="Edit">
					<template #icon>
						<PenBox />
					</template>
				</Button>
				<Button severity="danger" class="w-26" label="Delete"
					@click="confirmDelete(Number(route.params.jo_number))">
					<template #icon>
						<Trash />
					</template>
				</Button>
			</div>
		</section>
		<div class="mt-6 overflow-y-auto h-[calc(100vh-8rem)]">
			<section class="grid grid-cols-2 bg-white rounded-2xl border border-slate-200 p-4">
				<div>
					<p class="font-medium text-sm text-slate-600">Job Order</p>
					<p class="font-semibold text-xl">#{{ jobOrder?.jo_number }}</p>
					<div class="mt-3 flex flex-col gap-1">
						<p class="font-medium text-slate-800">{{ jobOrder?.customer_name }}</p>
						<div class="flex flex-wrap gap-x-4 gap-y-1">
							<div class="flex items-center gap-1.5 text-slate-600">
								<Mail class="size-5 shrink-0" />
								<span>{{ jobOrder?.customer_email ?? '—' }}</span>
							</div>
							<div class="flex items-center gap-1.5 text-slate-600">
								<Phone class="size-5 shrink-0" />
								<span>{{ jobOrder?.customer_contact_no ?? '—' }}</span>
							</div>
						</div>
					</div>
				</div>
				<div class="flex flex-col items-end">
					<Tag rounded class="w-30" :value="jobOrder?.payment_status" />
					<div class="flex-1 flex flex-col items-end justify-end">
						<p class="text-slate-600">Started on {{ formatDate(jobOrder?.date_received) }}</p>
						<p class="text-slate-500">Created by {{ jobOrder?.created_by_name }} on {{
							formatDate(jobOrder?.created_at) }}</p>
						<p class="text-slate-500">Last Updated by {{ jobOrder?.updated_by_name }} on {{
							formatDate(jobOrder?.updated_at) }}</p>
					</div>
				</div>
			</section>
			<section class="mt-6">
				<div class="grid grid-cols-3 gap-6">
					<div class="bg-white rounded-2xl border border-slate-200 p-4">
						<p class="text-slate-600">Total Due</p>
						<p class="text-slate-800 text-xl font-medium">{{ formatCurrency(jobOrder?.total_due) }}</p>
					</div>
					<div class="bg-white rounded-2xl border border-slate-200 p-4">
						<p class="text-slate-600">Total Paid</p>
						<p class="text-slate-800 text-xl font-medium">{{ formatCurrency(jobOrder?.total_paid) }}</p>
					</div>
					<div class="bg-white rounded-2xl border border-slate-200 p-4">
						<p class="text-slate-600">Balance</p>
						<p :class="(jobOrder?.total_due ?? 0) - (jobOrder?.total_paid ?? 0) > 0 ? 'text-amber-600' : 'text-slate-800'"
							class="text-xl font-medium">
							{{ formatCurrency((jobOrder?.total_due ?? 0) - (jobOrder?.total_paid ?? 0)) }}
						</p>
					</div>
				</div>
			</section>
			<section class="mt-6">
				<JobItemsList :items="jobOrder?.job_items ?? []" :jo_number="Number(jobOrder?.jo_number ?? 0)"
					:readOnly="true" />
			</section>
			<section class="mt-6 grid grid-cols-2 gap-6">
				<PaymentsTable :payments="(jobOrder?.payments ?? []) as Payment[]"
					:jobItems="(jobOrder?.job_items ?? []) as JobItemFromDB[]" :readOnly="true" />
				<ClaimsTable :claims="(jobOrder?.claims ?? []) as ClaimingHistory[]"
					:jobItems="(jobOrder?.job_items ?? []) as JobItemFromDB[]" :readOnly="true" />
			</section>
		</div>
	</div>
</template>