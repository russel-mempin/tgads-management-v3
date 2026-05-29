<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { JobOrder, JobItemCreate, PaymentCreate, ClaimCreate } from '@/types/job_orders'
import type { Customer } from '@/types/customers';
import { getJobOrder, editJobOrder } from '@/api/job_orders'
import { getCustomerNames, getCustomerInfo } from '@/api/customers';
import { Button, InputText, Select, InputNumber, DatePicker, useToast } from 'primevue';
import JobItemsList from '@/components/JobItemsList.vue';
import PaymentsTable from '@/components/PaymentsTable.vue';
import ClaimsTable from '@/components/ClaimsTable.vue';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const jobOrder = ref<JobOrder>();
const customerList = ref<string[]>([]);
const customerName = ref('');
const isNewCustomer = ref(false);
const customerInfo = ref<Customer>({
	id: '',
	name: '',
	contact_no: '',
	email: '',
	address: ''
});
const jo_number = ref(0);
const date_received = ref(new Date());
const items = ref<JobItemCreate[]>([]);
const payments = ref<PaymentCreate[]>([]);
const claims = ref<ClaimCreate[]>([]);
onMounted(async () => {
	const [orderData, names] = await Promise.all([
		getJobOrder(route.params.jo_number as string),
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
    items.value = data.job_items as unknown as JobItemCreate[]
    payments.value = data.payments as unknown as PaymentCreate[]
    // Map claims to use item_id instead of UUID job_item_id
    claims.value = data.claims.map(c => ({
        ...c,
        job_item_id: c.claimed_item_id  // use human-readable item_id
    })) as unknown as ClaimCreate[]
})
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

const buildPayload = () => {
	return {
		jo_number: String(jo_number.value),
		date_received: date_received.value.toISOString(),
		...(isNewCustomer.value ? {
			customer_name: customerInfo.value.name,
			customer_address: customerInfo.value.address,
			customer_contact_no: customerInfo.value.contact_no,
			customer_email: customerInfo.value.email,
		} : {
			customer_id: customerInfo.value.id,
		}),
		job_items: items.value.map(item => ({
			jo_number: String(jo_number.value),
			item_id: item.item_id,
			description: item.description,
			height: item.height,
			width: item.width,
			size_unit: item.size_unit,
			paper_size: item.paper_size,
			quantity: item.quantity,
			job_status: item.job_status,
			due_date: new Date(item.due_date).toISOString(),
			discount: item.discount,
			notes: item.notes,
			service_type_id: item.service_type_id,
			extra_type_id: item.extra_type_id ?? null,
		})),
		...(payments.value.length ? {
			payments: payments.value.map(p => ({
				date_received: new Date(p.date_received).toISOString(),
				method: p.method,
				amount: p.amount,
			}))
		} : {}),
		...(claims.value.length ? {
			claims: claims.value.map(c => ({
				date_claimed: new Date(c.date_claimed).toISOString(),
				name: c.name,
				pcs_claimed: c.pcs_claimed,
				claimed_item_id: c.claimed_item_id,
			}))
		} : {}),
	}
}

const handleSave = async () => {
	try {
		const payload = buildPayload()
		await editJobOrder(route.params.jo_number as string, payload)
		toast.add({ severity: 'success', summary: 'Saved', detail: 'Job order updated successfully.', life: 3000 })
		router.push('/admin/job-orders')
	} catch (error: any) {
		console.error(error.response?.data || error)
		toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update job order.', life: 3000 })
	}
}
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-xl font-semibold">Edit Job Order</h1>
			<h2>Update information of a Job Order upon saving.</h2>
		</div>
		<div class="flex gap-4">
			<Button severity="info" class="w-26" label="Save" @click="handleSave" />
		</div>
	</section>
	<div class="mt-4 overflow-y-auto h-[calc(100vh-8rem)]">
		<section class="mt-4 flex flex-col">
			<label class="mb-1 text-slate-700 font-medium">Customer Name</label>
			<Select v-model="customerName" fluid editable :options="customerList"
				placeholder="Select or input a customer" class="w-full md:w-56" />
			<div class="mt-2 grid grid-cols-3 gap-2">
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Address</label>
					<InputText v-model="customerInfo.address" placeholder="Address" :disabled="!isNewCustomer" />
				</div>
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Contact No.</label>
					<InputText v-model="customerInfo.contact_no" placeholder="Contact No." :disabled="!isNewCustomer" />
				</div>
				<div class="flex flex-col">
					<label class="mb-1 text-slate-700 font-medium">Email</label>
					<InputText v-model="customerInfo.email" placeholder="Email" :disabled="!isNewCustomer" />
				</div>
			</div>
		</section>
		<section class="mt-2 grid grid-cols-2 gap-2">
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
		<section class="mt-4 rounded-md border border-slate-300">
			<JobItemsList v-model:items="items" :jo_number="jo_number" :readOnly="false" />
		</section>
		<section class="mt-4 grid grid-cols-2 gap-4">
			<PaymentsTable v-model:payments="payments" :jobItems="items" :readOnly="false" />
			<ClaimsTable v-model:claims="claims" :jobItems="items" />
		</section>
	</div>
</template>