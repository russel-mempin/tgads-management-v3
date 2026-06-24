<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowLeft, Save } from '@lucide/vue';
import type { JobOrder, JobItemPayload, Payment, ClaimingHistory, JobOrderCreate } from '@/types/job_orders'
import type { Customer } from '@/types/customers';
import { getJobOrder, editJobOrder } from '@/api/job_orders'
import { getCustomerNames, getCustomerInfo } from '@/api/customers';
import { Button, InputText, Select, InputNumber, DatePicker, useToast } from 'primevue';
import JobItemsList from '@/components/JobItemsList.vue';
import PaymentsTable from '@/components/PaymentsTable.vue';
import ClaimsTable from '@/components/ClaimsTable.vue';
import { formatCurrency } from '@/utils/formatters';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const jobOrder = ref<JobOrder>();
const customerList = ref<string[]>([]);
const customerName = ref('');
const isNewCustomer = ref(false);
const customerInfo = ref<Customer>({
	name: '',
	contact_no: '',
	email: '',
	address: ''
});
const jo_number = ref(0);
const date_received = ref(new Date());
const items = ref<JobItemPayload[]>([]);
const payments = ref<Payment[]>([]);
const claims = ref<ClaimingHistory[]>([]);
onMounted(async () => {
	const [orderData, names] = await Promise.all([
		getJobOrder(Number(route.params.jo_number)),
		getCustomerNames()
	])
	customerList.value = names
	jobOrder.value = orderData
})
watch(jobOrder, (data) => {
	if (!data) return
	customerName.value = data.customer_name
	jo_number.value = Number(data.jo_number)
	date_received.value = new Date(data.date_received)
	items.value = data.job_items as unknown as JobItemPayload[]
	payments.value = data.payments as unknown as Payment[]
	// Map claims to use item_id instead of UUID job_item_id
	claims.value = data.claims.map(c => ({
		...c,
		job_item_id: c.claimed_item_id  // use human-readable item_id
	})) as unknown as ClaimingHistory[]
})
watch(customerName, async (name) => {
	if (!name) {
		customerInfo.value = {
			name: '',
			contact_no: '',
			email: '',
			address: '',
		};
		return;
	}
	const exists = customerList.value.some(
		(c) => c.toLowerCase() === name.toLowerCase()
	);
	if (exists) {
		// Autofill from backend
		isNewCustomer.value = false;
		const data = await getCustomerInfo(name);
		if (data) customerInfo.value = data;
	} else {
		// New customer — clear fields
		isNewCustomer.value = true;
		customerInfo.value = { name, contact_no: '', email: '', address: '' };
	}
});

const totalDue = computed(() =>
	items.value.reduce((sum: number, item: JobItemPayload) =>
		sum + (item.unit_price + item.extra_service_price - item.discount) * item.quantity, 0)
)

const totalPaid = computed(() =>
	payments.value.reduce((sum: number, p) => sum + p.amount, 0)
)

const buildPayload = () => {
	const payload = {
		jo_number: jo_number.value,
		date_received: date_received.value,
		customer_name: customerInfo.value.name,
		customer_address: customerInfo.value.address,
		customer_contact_no: customerInfo.value.contact_no,
		customer_email: customerInfo.value.email,

		job_items: items.value.map(item => ({
			jo_number: jo_number.value,
			item_id: item.item_id,
			description: item.description,
			height: item.height,
			width: item.width,
			size_unit: item.size_unit,
			quantity: item.quantity,
			job_status: item.job_status,
			due_date: new Date(item.due_date),
			discount: item.discount,
			extra_charge: item.extra_charge,
			notes: item.notes,
			service_name: item.service_name,
			extra_service_name: item.extra_service_name ?? null,
		})),

		...(payments.value.length ? {
			payments: payments.value.map(p => ({
				date_received: new Date(p.date_received),
				method: p.method,
				amount: p.amount,
			}))
		} : {}),

		...(claims.value.length ? {
			claims: claims.value.map(c => ({
				date_claimed: new Date(c.date_claimed),
				name: c.name,
				pcs_claimed: c.pcs_claimed,
				claimed_item_id: c.claimed_item_id,
			}))
		} : {}),
	}
	handleSave(payload)
}

const handleSave = async (payload: JobOrderCreate) => {
	try {
		await editJobOrder(Number(route.params.jo_number), payload)
		toast.add({ severity: 'success', summary: 'Saved', detail: 'Job order updated successfully.', life: 3000 })
		router.push('/admin/job-orders')
	} catch (error: any) {
		console.error(error.response?.data || error)
		toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update job order.', life: 3000 })
	}
}
</script>

<template>
	<div class="mx-12 my-6 flex flex-col h-full min-h-0">
		<section class="mb-6 flex-shrink-0">
			<div>
				<h1 class="text-xl font-semibold">Edit Job Order</h1>
				<h2>Update information of a Job Order upon saving.</h2>
			</div>
			<div class="mt-1 flex items-center">
				<p class="text-gray-500 font-medium">Fields marked with</p>
				<p class="text-red-500 font-medium">&nbsp;*&nbsp;</p>
				<p class="text-gray-500 font-medium">are required.</p>
			</div>
		</section>
		<div class="flex-1 overflow-y-auto min-h-0 pr-1">
			<!-- Customer Name Search -->
			<section>
				<div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
					<div>
						<label class="mb-1 text-slate-700 font-medium">Customer Name <span class="text-sm text-red-500">
								* </span> </label>
						<Select v-model="customerName" fluid editable :options="customerList"
							placeholder="Select or input a customer" class="w-full md:w-56" :pt="{
								option: ({ context }) => ({
									class: context.selected
										? '!bg-blue-600 !text-white !font-semibold'
										: context.focused
											? '!bg-blue-50 !text-blue-700 !font-semibold'
											: ''
								})
							}" />
						<p class="text-sm font-medium text-gray-500 mt-1">Start typing to search saved customers, or
							enter a
							new
							name to
							add one.</p>
					</div>
					<div class="mt-4 grid grid-cols-3 gap-6">
						<div class="flex flex-col">
							<label class="mb-1 text-slate-700 font-medium">Address</label>
							<InputText v-model="customerInfo.address" placeholder="Address"
								:disabled="!isNewCustomer" />
						</div>
						<div class="flex flex-col">
							<label class="mb-1 text-slate-700 font-medium">Contact No.</label>
							<InputText v-model="customerInfo.contact_no" placeholder="Contact No."
								:disabled="!isNewCustomer" />
						</div>
						<div class="flex flex-col">
							<label class="mb-1 text-slate-700 font-medium">Email</label>
							<InputText v-model="customerInfo.email" placeholder="Email" :disabled="!isNewCustomer" />
						</div>
					</div>
				</div>
			</section>
			<!-- Job Order Metadata -->
			<section class="mt-6 grid grid-cols-2 gap-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">JO Number</label>
					<InputNumber v-model="jo_number" placeholder="JO Number" :useGrouping="false" fluid
						:disabled="items.length > 0"
						v-tooltip.top="{ value: 'Clear all job items to change the JO Number.', disabled: items.length === 0 }" />
				</div>
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Date Received</label>
					<DatePicker v-model="date_received" :maxDate="new Date()" showTime hourFormat="12" />
				</div>
			</section>
			<section class="mt-6">
				<JobItemsList v-model:items="items" :jo_number="jo_number" :readOnly="false" />
			</section>
			<section class="mt-6 grid grid-cols-2 gap-6">
				<PaymentsTable v-model:payments="payments" :jobItems="items" :readOnly="false" />
				<ClaimsTable v-model:claims="claims" :jobItems="items" />
			</section>
		</div>
	</div>
	<!-- Sticky Footer -->
	<div
		class="sticky bottom-0 bg-white border-t border-gray-200 shadow-md px-6 py-4 flex items-center justify-between">
		<div class="flex gap-8">
			<div>
				<p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Due</p>
				<p class="text-lg font-semibold text-gray-800">{{ formatCurrency(totalDue) }}</p>
			</div>
			<div>
				<p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Paid</p>
				<p class="text-lg font-semibold text-gray-800">{{ formatCurrency(totalPaid) }}</p>
			</div>
			<div>
				<p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Balance</p>
				<p class="text-lg font-semibold"
					:class="totalDue - totalPaid > 0 ? 'text-amber-600' : 'text-green-600'">
					{{ formatCurrency(totalDue - totalPaid) }}
				</p>
			</div>
		</div>
		<div class="flex gap-4">
			<Button class="w-48" variant="outlined" label="Back" iconPos="left"
				@click="router.push('/admin/job-orders/')" :pt="{ label: { class: 'flex-1 text-center' } }">
				<template #icon>
					<ArrowLeft />
				</template>
			</Button>
			<Button class="w-48" label="Save Job Order" iconPos="left" @click="buildPayload"
				:pt="{ label: { class: 'flex-1 text-center' } }">
				<template #icon>
					<Save />
				</template>
			</Button>
		</div>
	</div>
</template>