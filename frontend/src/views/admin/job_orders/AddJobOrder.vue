<script setup lang="ts">
// AddJobOrder.vue
import { ref, onMounted, watch } from 'vue';
import { Button, Select, InputText, InputNumber, DatePicker, useToast } from 'primevue';
import { useRouter } from 'vue-router';
import { ArrowLeft, Save } from '@lucide/vue';
import { getCustomerNames, getCustomerInfo } from '@/api/customers';
import type { Customer } from '@/types/customers';
import type { JobItemCreate, PaymentCreate, ClaimCreate, JobOrderCreate } from '@/types/job_orders';
import JobItemsList from '@/components/JobItemsList.vue';
import PaymentsTable from '@/components/PaymentsTable.vue';
import ClaimsTable from '@/components/ClaimsTable.vue';
import { createJobOrder } from '@/api/job_orders';

const toast = useToast()
const router = useRouter()
const customerList = ref<string[]>([]);
onMounted(async () => {
	customerList.value = await getCustomerNames()
});

const customerName = ref('');
const isNewCustomer = ref(false);
const customerInfo = ref<Customer>({
	id: '',
	name: '',
	contact_no: '',
	email: '',
	address: ''
});

watch(customerName, async (name) => {
	if (!name) {
		customerInfo.value = {
			id: '',
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
		customerInfo.value = { id: '', name, contact_no: '', email: '', address: '' };
	}
});

const jo_number = ref(0);
const date_received = ref(new Date());
const items = ref<JobItemCreate[]>([]);
const payments = ref<PaymentCreate[]>([]);
const claims = ref<ClaimCreate[]>([]);

const buildPayload = () => {
	const payload = {
		jo_number: jo_number.value,

		date_received: date_received.value.toISOString(),

		...(isNewCustomer.value
			? {
				customer_name: customerInfo.value.name,
				customer_address: customerInfo.value.address,
				customer_contact_no: customerInfo.value.contact_no,
				customer_email: customerInfo.value.email,
			}
			: {
				customer_id: customerInfo.value.id,
			}),

		job_items: items.value.map(item => ({
			jo_number: jo_number.value,
			item_id: item.item_id,
			description: item.description,
			height: item.height,
			width: item.width,
			size_unit: item.size_unit,
			quantity: item.quantity,
			job_status: item.job_status,
			due_date: new Date(item.due_date).toISOString(),
			discount: item.discount,
			notes: item.notes,
			service_type_id: item.service_type_id,
			extra_type_id: item.extra_type_id ?? null,
		})),
		...(payments.value.length ? {
			payments: payments.value.map(payment => ({
				date_received: new Date(payment.date_received).toISOString(),
				method: payment.method,
				amount: payment.amount,
			}))
		} : {}),

		...(claims.value.length ? {
			claims: claims.value.map(claim => ({
				date_claimed: new Date(claim.date_claimed).toISOString(),
				name: claim.name,
				pcs_claimed: claim.pcs_claimed,
				claimed_item_id: claim.claimed_item_id,
			}))
		} : {}),
	};

	handleSave(payload);
};

const handleSave = async (payload: JobOrderCreate) => {
	try {
		await createJobOrder(payload)
		toast.add({
			severity: 'success',
			summary: 'Order saved',
			detail: 'Order data has been added to the database',
			life: 3000,
		})
		router.push('/admin/job-orders')
	}
	catch (error: any) {
		console.error(error.response?.data || error)
		toast.add({
			severity: 'error',
			summary: 'Error',
			detail: 'Failed to save order data.',
			life: 3000,
		})
	}
}
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-xl font-semibold">Add Job Order</h1>
			<h2 class="text-gray-800">Fill in the details below to create a new job order.</h2>
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
	</section>
	<section class="my-4 flex items-center">
		<p class="text-gray-500 font-medium">Fields marked with</p>
		<p class="text-red-500 font-medium">&nbsp;*&nbsp;</p>
		<p class="text-gray-500 font-medium">are required.</p>
	</section>
	<!-- Customer Name Search -->
	<section>
		<div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
			<div>
				<label class="mb-1 text-slate-700 font-medium">Customer Name</label>
				<span class="text-sm text-red-500"> * </span>
				<Select v-model="customerName" fluid editable :options="customerList"
					placeholder="Select or input a customer" class="w-full md:w-56" />
				<p class="text-sm font-medium text-gray-500 mt-1">Start typing to search saved customers, or enter a new
					name to
					add one.</p>
			</div>
			<div class="mt-4 grid grid-cols-3 gap-6">
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Address</label>
					<InputText v-model="customerInfo.address" placeholder="House/Unit No., Street, City"
						:disabled="!isNewCustomer" />
				</div>
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Contact No.</label>
					<InputText v-model="customerInfo.contact_no" placeholder="09XX XXX XXXX"
						:disabled="!isNewCustomer" />
				</div>
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Email</label>
					<InputText v-model="customerInfo.email" placeholder="name@email.com" :disabled="!isNewCustomer" />
				</div>
			</div>
		</div>
	</section>
	<!-- Job Order Metadata -->
	<section class="mt-4 grid grid-cols-2 gap-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
		<div class="flex flex-col">
			<div class="flex">
				<label class="mb-1 text-slate-700 font-medium">Job Order No.</label>
				<span class="text-sm text-red-500">&nbsp;*</span>
			</div>
			<InputNumber v-model="jo_number" placeholder="JO Number" :useGrouping="false" fluid
				:disabled="items.length > 0"
				v-tooltip.top="{ value: 'Clear all job items to change the JO Number.', disabled: items.length === 0 }" />
		</div>
		<div class="flex flex-col">
			<div class="flex">
				<label class="mb-1 text-slate-700 font-medium">Date Received</label>
				<span class="text-sm text-red-500">&nbsp;*</span>
			</div>
			<DatePicker v-model="date_received" :maxDate="new Date()" showTime hourFormat="12" />
		</div>
	</section>
	<section class="mt-4 rounded-md border border-slate-300">
		<JobItemsList v-model:items="items" :jo_number="jo_number" :readOnly="false" />
	</section>
	<section class="mt-4 grid grid-cols-2 gap-4">
		<PaymentsTable v-model:payments="payments" :jobItems="items" :readOnly="false" />
		<ClaimsTable v-model:claims="claims" :jobItems="items" />
	</section>
</template>