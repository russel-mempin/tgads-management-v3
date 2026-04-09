<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Button, InputText, Select, DataTable, Column, Tag } from 'primevue';
import { Plus } from '@lucide/vue';
import { getAllJobOrders } from '@/api/job_orders'
import type { JobOrders } from '@/types/job_orders'
import { formatCurrency, formatDate } from '@/utils/formatters';

const job_orders = ref<JobOrders[]>([])
onMounted(async () => {
	const data = await getAllJobOrders()
	job_orders.value = data
	console.log(job_orders.value)
})

const joNumberSearch = ref('');
const jobStatus = ref('');
const jobStatusOptions = ref(['For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled']);
const expandedRows = ref({});

// Code for determining status' design
const mapSeverity = (status: string) => {
	switch (status) {
		case "For Layout":
			return "warn";
		case "Partial":
			return "warn";
		case "For Approval":
			return "info";
		case "For Pickup":
			return "info";
		case "Released":
			return "success";
		case "Fully Paid":
			return "success";
		case "Cancelled":
			return "danger";
		case "Unpaid":
			return "danger";
		case "Credit":
			return "danger";
		case "Refunded":
			return "danger";
		default:
			return "contrast";
	}
};
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Job Orders</h1>
			<h2>View and manage all job orders in the system. Filter data to quickly find relevant orders.</h2>
		</div>
		<Button label="Add Job Order">
			<template #icon>
				<Plus />
			</template>
		</Button>
	</section>
	<section class="my-2 flex gap-2">
		<InputText class="flex-1" v-model="joNumberSearch" placeholder="Search by customer name or JO Number..." />
		<Select v-model="jobStatus" :options="jobStatusOptions" placeholder="Job Status" />
		<Button label="Clear Filters" variant="text">
		</Button>
	</section>
	<section class="flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
		<DataTable 
			scrollable
			scroll-height="flex"
			:pt="{ root: 'h-full' }"
			v-model:expandedRows="expandedRows" 
			:value="job_orders" 
			dataKey="id" 
			tableStyle="min-width: 60rem;" 
			paginator :rows="5" 
			:rowsPerPageOptions="[5, 10, 20, 50]"
		>
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
			<Column field="total_due" header="Total Due">
				<template #body="slotProps">
					{{ formatCurrency(slotProps.data.total_due) }}
				</template>
			</Column>
			<Column field="total_paid" header="Total Paid">
				<template #body="slotProps">
					{{ formatCurrency(slotProps.data.total_paid) }}
				</template>
			</Column>
			<template #expansion="slotProps">
				<div class="p-4">
					<h5>Job items of JO Number {{ slotProps.data.jo_number }}</h5>
					<DataTable :value="slotProps.data.job_items">
						<Column field="item_id" header="ID"></Column>
						<Column field="service_name" header="Service"></Column>
						<Column field="description" header="Description"></Column>
						<Column field="height" header="Height"></Column>
						<Column field="width" header="Width"></Column>
						<Column field="size_unit" header="Unit"></Column>
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
						<Column field="extra_service_name" header="Extra"></Column>
						<Column field="extra_service_price" header="Price">
							<template #body="slotProps">
								{{ formatCurrency(slotProps.data.extra_service_price) }}
							</template>
						</Column>
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
				<div class="p-4">
					<h5>Payments of {{ slotProps.data.customer_name }}</h5>
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
					</DataTable>
				</div>
				<div class="p-4">
					<h5>Claiming History of {{ slotProps.data.customer_name }}</h5>
					<DataTable :value="slotProps.data.claims">
						<Column field="date_claimed" header="Date claimed">
							<template #body="slotProps">
								{{ formatDate(slotProps.data.date_claimed) }}
							</template>
						</Column>
						<Column field="name" header="Name"></Column>
						<Column field="pcs_claimed" header="Pcs. claimed"></Column>
					</DataTable>
				</div>
			</template>
		</DataTable>
	</section>
</template>