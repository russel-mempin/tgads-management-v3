<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { RouterLink, useRouter } from 'vue-router'
import { Button, InputText, Select, DataTable, Column, Tag } from 'primevue';
import { Plus, PhilippinePeso, Clock, TrendingUp } from '@lucide/vue';
import { getAllJobOrders, getJobOrderCount, getJobOrderKpis } from '@/api/job_orders'
import type { JobOrder } from '@/types/job_orders'
import { formatCurrency, formatDateNoYear, mapSeverity, mapCustomColor } from '@/utils/formatters';

const job_orders = ref<JobOrder[]>([])
const router = useRouter()
const totalRecords = ref(0)
const loading = ref(false)
const rows = ref(20)
const currentOffset = ref(0)

const joNumberSearch = ref('');
const jobStatus = ref('');
const paymentStatus = ref('');
const paymentStatusOptions = ref(['Fully Paid', 'Partial', 'Unpaid', 'Credit', 'Refunded', 'Overcharged']);
const jobStatusOptions = ref(['Pending', 'For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled']);
const expandedRows = ref<Record<string, boolean>>({})
const kpis = ref({
	outstanding_balance: 0,
	unpaid_count: 0,
	overdue_count: 0,
	payments_this_week: 0,
})

const fetchServices = async () => {
    loading.value = true
    const filterParams = {
        offset: currentOffset.value,
        limit: rows.value,
        payment_status: paymentStatus.value || undefined,
        job_status: jobStatus.value || undefined,
        search: joNumberSearch.value || undefined,
        filter: activeFilter.value || undefined,
    }
    const [data, count] = await Promise.all([
        getAllJobOrders(filterParams),
        getJobOrderCount(filterParams)
    ])
    job_orders.value = data
    totalRecords.value = count
    loading.value = false
}

const onPage = (event: any) => {
	currentOffset.value = event.first
	rows.value = event.rows
	fetchServices()
}

let debounceTimer: ReturnType<typeof setTimeout>
watch([joNumberSearch, jobStatus, paymentStatus], () => {
	clearTimeout(debounceTimer)
	debounceTimer = setTimeout(() => {
		currentOffset.value = 0
		fetchServices()
	}, 300)
})

onMounted(async () => {
	fetchServices()
	kpis.value = await getJobOrderKpis()
})

const clearFilters = () => {
	joNumberSearch.value = ''
	jobStatus.value = ''
	paymentStatus.value = ''
	currentOffset.value = 0
	fetchServices()
}

const printJobOrder = (jo_number: string) => {
	window.open(`/job-orders/print/${jo_number}`, '_blank')
}

const onRowClick = (event: { data: JobOrder }) => {
	const isExpanded = expandedRows.value[event.data.id]
	if (isExpanded) {
		delete expandedRows.value[event.data.id]
	} else {
		expandedRows.value[event.data.id] = true
	}
}

const activeFilter = ref<string | null>(null)

const setFilter = (filter: string) => {
    activeFilter.value = activeFilter.value === filter ? null : filter
    clearFilters()
}
</script>

<template>
	<div class="mx-12 my-6 flex flex-col h-full min-h-0 overflow-hidden">
		<!-- Page Title -->
		<section class="flex justify-between items-center">
			<div>
				<h1 class="text-xl font-semibold">Job Orders</h1>
				<h2 clsas="text-gray-800">View and manage all job orders in the system. Filter data to quickly find
					relevant
					orders.</h2>
			</div>
			<RouterLink to="/admin/job-orders/add">
				<Button label="Add Job Order">
					<template #icon>
						<Plus />
					</template>
				</Button>
			</RouterLink>
		</section>
		<!-- Summary Bar -->
		<section class="my-6 grid grid-cols-4 gap-6">
			<div @click="setFilter('outstanding')"
				class="border border-gray-200 shadow-xs p-4 rounded-xl flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
				:class="activeFilter === 'outstanding' ? 'bg-orange-100' : 'bg-white hover:bg-orange-50'">
				<div class="flex items-center justify-center w-12 h-12 rounded-full text-orange-700"
					:class="activeFilter === 'outstanding' ? 'bg-orange-300' : 'bg-orange-100'">
					<PhilippinePeso />
				</div>
				<div class="ml-4">
					<p class="uppercase font-semibold text-sm text-gray-600">Outstanding Balance</p>
					<p class="font-bold text-3xl text-orange-700">{{ formatCurrency(kpis.outstanding_balance) }}</p>
				</div>
			</div>
			<div @click="setFilter('unpaid')"
				class="border border-gray-200 shadow-xs p-4 rounded-xl flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
				:class="activeFilter === 'unpaid' ? 'bg-red-100' : 'bg-white hover:bg-red-50'">
				<div class="flex items-center justify-center w-12 h-12 rounded-full text-red-700"
					:class="activeFilter === 'unpaid' ? 'bg-red-300' : 'bg-red-100'">
					<Clock />
				</div>
				<div class="ml-4">
					<p class="uppercase font-semibold text-sm text-gray-600">Unpaid Orders</p>
					<p class="font-bold text-3xl text-red-700">{{ kpis.unpaid_count }}</p>
				</div>
			</div>
			<div @click="setFilter('overdue')"
				class="border border-gray-200 shadow-xs p-4 rounded-xl flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
				:class="activeFilter === 'overdue' ? 'bg-red-100' : 'bg-white hover:bg-red-50'">
				<div class="flex items-center justify-center w-12 h-12 rounded-full text-red-700"
					:class="activeFilter === 'overdue' ? 'bg-red-300' : 'bg-red-100'">
					<Clock />
				</div>
				<div class="ml-4">
					<p class="uppercase font-semibold text-sm text-gray-600">Overdue Items</p>
					<p class="font-bold text-3xl text-red-700">{{ kpis.overdue_count }}</p>
				</div>
			</div>
			<div @click="setFilter('payments-week')"
				class="border border-gray-200 shadow-xs p-4 rounded-xl flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
				:class="activeFilter === 'payments-week' ? 'bg-green-100' : 'bg-white hover:bg-green-50'">
				<div class="flex items-center justify-center w-12 h-12 rounded-full text-green-700"
					:class="activeFilter === 'payments-week' ? 'bg-green-300' : 'bg-green-100'">
					<TrendingUp />
				</div>
				<div class="ml-4">
					<p class="uppercase font-semibold text-sm text-gray-600">Collected This Week</p>
					<p class="font-bold text-3xl text-green-700">{{ formatCurrency(kpis.payments_this_week) }}</p>
				</div>
			</div>
		</section>
		<!-- Filters -->
		<section class="mb-4 flex gap-6">
			<InputText class="flex-1" v-model="joNumberSearch" placeholder="Search by customer name or JO Number..." />
			<Select class="w-50" v-model="jobStatus" :options="jobStatusOptions" placeholder="Job Status" showClear />
			<Select class="w-50" v-model="paymentStatus" :options="paymentStatusOptions" placeholder="Payment Status"
				showClear />
			<Button :pt="{ label: '!font-semibold', }" label="Clear Filters" variant="text" @click="clearFilters" />
		</section>
		<!-- Table-->
		<section class="flex-1 min-h-0 rounded-md border border-slate-300 overflow-hidden bg-white">
			<DataTable class="main-job-orders-table" scrollable scroll-height="flex" :pt="{ root: 'h-full' }"
				v-model:expandedRows="expandedRows" :lazy="true" :rows="rows" :totalRecords="totalRecords"
				:loading="loading" :first="currentOffset" @page="onPage" :value="job_orders" dataKey="id"
				tableStyle="min-width: 60rem;" paginator :rowsPerPageOptions="[5, 10, 20, 50]" @row-click="onRowClick">
				<Column expander style="width: 5rem" />
				<Column field="jo_number" header="JO Number"></Column>
				<Column field="customer_name" header="Customer"></Column>
				<Column field="date_received" header="Start Date">
					<template #body="slotProps">
						{{ formatDateNoYear(slotProps.data.date_received) }}
					</template>
				</Column>
				<Column field="updated_at" header="Last Update">
					<template #body="slotProps">
						{{ formatDateNoYear(slotProps.data.updated_at) }}
					</template>
				</Column>
				<Column field="payment_status" header="Payment Status">
					<template #body="slotProps">
						<Tag :value="slotProps.data.payment_status"
							:severity="mapCustomColor(slotProps.data.payment_status) ? undefined : mapSeverity(slotProps.data.payment_status)"
							:class="mapCustomColor(slotProps.data.payment_status)" />
					</template>
				</Column>
				<Column field="overall_job_status" header="Overall Job Status">
					<template #body="{ data }">
						<Tag :value="data.overall_job_status"
							:severity="mapCustomColor(data.overall_job_status) ? undefined : mapSeverity(data.overall_job_status)"
							:class="mapCustomColor(data.overall_job_status)" />
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
							<Button class="w-18 h-10" variant="outlined" label="View"
								@click.stop="router.push(`/admin/job-orders/view/${data.jo_number}`)" />
							<Button class="w-18 h-10" variant="text" :pt="{ label: '!text-gray-500', }" label="Print"
								@click.stop="printJobOrder(data.jo_number)" />
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
							<Column header="Item">
								<template #body="{ data }">
									<span>{{ data.service_name }}</span>
									<span>{{ data.description ? ` - ${data.description}` : '' }}</span>
									<span>{{ data.extra_service_name ? ` w/ ${data.extra_service_name}` : '' }}</span>
								</template>
							</Column>
							<Column header="Dimensions">
								<template #body="{ data }">
									{{ (data.height && data.width) ? `${data.height} × ${data.width} ${data.size_unit}`
										:
										'—' }}
								</template>
							</Column>
							<Column field="quantity" header="Qty."></Column>
							<Column field="due_date" header="Due Date">
								<template #body="slotProps">
									<div class="flex items-center gap-2">
										{{ formatDateNoYear(slotProps.data.due_date) }}
										<span
											v-if="new Date(slotProps.data.due_date) < new Date() && slotProps.data.job_status !== 'Released' && slotProps.data.job_status !== 'Cancelled' && slotProps.data.job_status !== 'For Pickup' && slotProps.data.job_status !== 'For Approval'"
											class="text-xs font-medium text-red-500">
											Overdue
										</span>
									</div>
								</template>
							</Column>
							<Column field="job_status" header="Status">
								<template #body="slotProps">
									<Tag :value="slotProps.data.job_status"
										:severity="mapCustomColor(slotProps.data.job_status) ? undefined : mapSeverity(slotProps.data.job_status)"
										:class="mapCustomColor(slotProps.data.job_status)" />
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
									{{ formatDateNoYear(slotProps.data.date_received) }}
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
	</div>
</template>

<style scoped>
:deep(.p-datatable-row-expansion > td) {
	padding: 0 !important;
}

:deep(.main-job-orders-table > .p-datatable-table-container > table > .p-datatable-tbody > tr:hover) {
	background-color: #f1f5f9;
	cursor: pointer;
}
</style>