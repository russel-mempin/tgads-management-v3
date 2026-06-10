<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { JobOrder, Payment, JobItem, ClaimingHistory } from '@/types/job_orders';
import { getJobOrder } from '@/api/job_orders';
import { Button, Tag, useConfirm, ConfirmDialog, useToast } from 'primevue';
import { Trash, PenBox, Mail, Phone } from '@lucide/vue';
import { formatDate, formatCurrency } from '@/utils/formatters';
import JobItemsList from '@/components/JobItemsList.vue';
import PaymentsTable from '@/components/PaymentsTable.vue';
import ClaimsTable from '@/components/ClaimsTable.vue';
import { Info } from '@lucide/vue';
import { archiveJobOrder } from '@/api/job_orders';

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();
const toast = useToast();
const jobOrder = ref<JobOrder>();
onMounted(async () => {
	jobOrder.value = await getJobOrder(route.params.jo_number as string)
});

const confirmDelete = (jo_number: string) => {
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
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-xl font-semibold">View Job Order</h1>
			<h2>See full information about a Job Order.</h2>
		</div>
		<div class="flex gap-4">
			<Button severity="warn" class="w-26" label="Edit">
				<template #icon>
					<PenBox />
				</template>
			</Button>
			<Button severity="danger" class="w-26" label="Delete"
				@click="confirmDelete(route.params.jo_number as string)">
				<template #icon>
					<Trash />
				</template>
			</Button>
		</div>
	</section>
	<div class="mt-4 overflow-y-auto h-[calc(100vh-8rem)]">
		<section class="flex flex-col bg-white rounded-md border border-slate-200 p-4">
			<div class="flex items-center justify-between">
				<p class="font-medium text-sm text-slate-600">Job Order</p>
				<Tag rounded class="w-24" :value="jobOrder?.payment_status" />
			</div>
			<div class="flex items-end justify-between">
				<p class="font-semibold text-xl">#{{ jobOrder?.jo_number }}</p>
				<p class="text-slate-600">Started on {{ formatDate(jobOrder?.date_received) }}</p>
			</div>

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
		</section>
		<section class="mt-4">
			<div class="grid grid-cols-3 gap-4">
				<div class="bg-white rounded-md border border-slate-200 p-4">
					<p class="text-slate-600">Total Due</p>
					<p class="text-slate-800 text-xl font-medium">{{ formatCurrency(jobOrder?.total_due) }}</p>
				</div>
				<div class="bg-white rounded-md border border-slate-200 p-4">
					<p class="text-slate-600">Total Paid</p>
					<p class="text-slate-800 text-xl font-medium">{{ formatCurrency(jobOrder?.total_paid) }}</p>
				</div>
				<div class="bg-white rounded-md border border-slate-200 p-4">
					<p class="text-slate-600">Balance</p>
					<p :class="(jobOrder?.total_due ?? 0) - (jobOrder?.total_paid ?? 0) > 0 ? 'text-amber-600' : 'text-slate-800'"
						class="text-xl font-medium">
						{{ formatCurrency((jobOrder?.total_due ?? 0) - (jobOrder?.total_paid ?? 0)) }}
					</p>
				</div>
			</div>
		</section>
		<section class="mt-4 rounded-md border border-slate-200">
			<JobItemsList :items="jobOrder?.job_items ?? []" :jo_number="Number(jobOrder?.jo_number ?? 0)"
				:readOnly="true" />
		</section>
		<section class="mt-4 grid grid-cols-2 gap-4">
			<PaymentsTable :payments="(jobOrder?.payments ?? []) as Payment[]"
				:jobItems="(jobOrder?.job_items ?? []) as JobItem[]" :readOnly="true" />
			<ClaimsTable :claims="(jobOrder?.claims ?? []) as ClaimingHistory[]"
				:jobItems="(jobOrder?.job_items ?? []) as JobItem[]" :readOnly="true" />
		</section>
	</div>
</template>