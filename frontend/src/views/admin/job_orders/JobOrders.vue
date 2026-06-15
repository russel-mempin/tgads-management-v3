<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RouterLink, useRouter } from 'vue-router'
import { Button, InputText, Select, DataTable, Column, Tag } from 'primevue';
import { Plus } from '@lucide/vue';
import { getAllJobOrders } from '@/api/job_orders'
import type { JobOrder } from '@/types/job_orders'
import { formatCurrency, formatDate, mapSeverity, getOverallJobStatus } from '@/utils/formatters';

const job_orders = ref<JobOrder[]>([])
const router = useRouter()
const fetchServices = async () => {
	job_orders.value = await getAllJobOrders()
	console.log("Fetch successful.")
}
onMounted(async () => {
	fetchServices()
});

const joNumberSearch = ref('');
const jobStatus = ref('');
const paymentStatus = ref('');
const paymentStatusOptions = ref(['Fully Paid', 'Partial', 'Unpaid', 'Credit', 'Refunded']);
const jobStatusOptions = ref(['For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled']);
const expandedRows = ref({});

const printJobOrder = (jo_number: string) => {
	window.open(`/job-orders/print/${jo_number}`, '_blank')
}

const filteredJobOrders = computed(() => {
	return job_orders.value.filter(jo => {
		const matchesSearch = joNumberSearch.value === '' ||
			jo.customer_name.toLowerCase().includes(joNumberSearch.value.toLowerCase()) ||
			jo.jo_number.toLowerCase().includes(joNumberSearch.value.toLowerCase())

		const matchesJobStatus = jobStatus.value === '' ||
			getOverallJobStatus(jo.job_items) === jobStatus.value

		const matchesPaymentStatus = paymentStatus.value === '' ||
			jo.payment_status === paymentStatus.value

		return matchesSearch && matchesJobStatus && matchesPaymentStatus
	})
})
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Job Orders</h1>
			<h2>View and manage all job orders in the system. Filter data to quickly find relevant orders.</h2>
		</div>
		<RouterLink to="/admin/job-orders/add">
			<Button label="Add Job Order">
				<template #icon>
					<Plus />
				</template>
			</Button>
		</RouterLink>
	</section>
	<section class="my-2 flex gap-2">
		<InputText class="flex-1" v-model="joNumberSearch" placeholder="Search by customer name or JO Number..." />
		<Select class="w-50" v-model="jobStatus" :options="jobStatusOptions" placeholder="Job Status" />
		<Select class="w-50" v-model="paymentStatus" :options="paymentStatusOptions" placeholder="Payment Status" />
		<Button label="Clear Filters" variant="text" @click="joNumberSearch = ''; jobStatus = ''; paymentStatus = ''" />
	</section>
	<section class="flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
		<DataTable scrollable scroll-height="flex" :pt="{ root: 'h-full' }" v-model:expandedRows="expandedRows"
			:value="filteredJobOrders" dataKey="id" tableStyle="min-width: 60rem;" paginator :rows="20"
			:rowsPerPageOptions="[5, 10, 20, 50]">
			<Column expander style="width: 5rem" />
			<Column field="jo_number" header="JO Number"></Column>
			<Column field="customer_name" header="Customer"></Column>
			<Column field="date_received" header="Start Date">
				<template #body="slotProps">
					{{ formatDate(slotProps.data.date_received) }}
				</template>
			</Column>
			<Column field="payment_status" header="Payment Status">
				<template #body="slotProps">
					<Tag :value="slotProps.data.payment_status" :severity="mapSeverity(slotProps.data.payment_status)">
					</Tag>
				</template>
			</Column>
			<Column field="job_status" header="Overall Job Status">
				<template #body="{ data }">
					<Tag :value="getOverallJobStatus(data.job_items)"
						:severity="mapSeverity(getOverallJobStatus(data.job_items))" />
				</template>
			</Column>
			<Column header="Balance">
				<template #body="slotProps">
					{{ formatCurrency(slotProps.data.total_due - slotProps.data.total_paid) }}
				</template>
			</Column>
			<Column>
				<template #body="{ data }">
					<div class="flex justify-self-end gap-2">
						<Button class="w-18 h-10" severity="info" label="View"
							@click="router.push(`/admin/job-orders/view/${data.jo_number}`)" />
						<Button class="w-18 h-10" severity="secondary" label="Print"
							@click="printJobOrder(data.jo_number)" />
					</div>
				</template>
			</Column>
			<template #empty>
				<div class="flex flex-col items-center justify-center py-2 text-slate-400">
					<p class="text-md">No data found.</p>
				</div>
			</template>
			<template #expansion="slotProps">
				<div class="bg-slate-100 p-4 border-l-4 border-slate-300">
					<h5 class="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
						Job Items — #{{ slotProps.data.jo_number }}
					</h5>
					<DataTable :value="slotProps.data.job_items">
						<Column field="item_id" header="ID"></Column>
						<Column field="description" header="Description"></Column>
						<Column header="Dimensions">
							<template #body="{ data }">
								{{ (data.height && data.width) ? `${data.height} × ${data.width} ${data.size_unit}` :
								'—' }}
							</template>
						</Column>
						<Column field="quantity" header="Qty."></Column>
						<Column field="due_date" header="Due Date">
							<template #body="slotProps">
								{{ formatDate(slotProps.data.due_date) }}
							</template>
						</Column>
						<Column field="job_status" header="Status">
							<template #body="slotProps">
								<Tag :value="slotProps.data.job_status"
									:severity="mapSeverity(slotProps.data.job_status)"></Tag>
							</template>
						</Column>
						<Column field="unit_price" header="Unit Price">
							<template #body="slotProps">
								{{ formatCurrency(slotProps.data.unit_price) }}
							</template>
						</Column>
						<Column field="extra_service_name" header="Extra Service"></Column>
						<Column field="discount" header="Discount">
							<template #body="slotProps">
								{{ formatCurrency(slotProps.data.discount) }}
							</template>
						</Column>
						<Column field="subtotal" header="Subtotal">
							<template #body="slotProps">
								{{ formatCurrency(slotProps.data.subtotal) }}
							</template>
						</Column>
					</DataTable>
				</div>
				<div class="bg-slate-100 p-4 border-l-4 border-slate-300">
					<h5 class="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
						Payments — {{ slotProps.data.customer_name }}
					</h5>
					<DataTable :value="slotProps.data.payments">
						<Column field="date_received" header="Date received">
							<template #body="slotProps">
								{{ formatDate(slotProps.data.date_received) }}
							</template>
						</Column>
						<Column field="method" header="Method"></Column>
						<Column field="amount" header="Amount">
							<template #body="slotProps">
								{{ formatCurrency(slotProps.data.amount) }}
							</template>
						</Column>
						<template #empty>
							<div class="flex flex-col items-center justify-center py-2 text-slate-400">
								<p class="text-md">No payments recorded for this job order.</p>
							</div>
						</template>
					</DataTable>
				</div>
			</template>
		</DataTable>
	</section>
</template>

<style scoped>
:deep(.p-datatable-row-expansion > td) {
	padding: 0 !important;
}
</style>