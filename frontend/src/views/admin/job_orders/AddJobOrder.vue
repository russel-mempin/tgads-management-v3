<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { Button, Select, InputText, InputNumber, DatePicker } from 'primevue';
import { Save } from '@lucide/vue';
import { getCustomerNames, getCustomerInfo } from '@/api/customers';
import { getAllServices } from '@/api/services';
import type { Customer } from '@/types/customers';
import type { JobItem } from '@/types/job_orders';
import type { ServiceType } from '@/types/services';
import JobItemsTable from '@/components/JobItemsTable.vue';

const customerList = ref<string[]>([]);
const serviceList = ref<ServiceType[]>([]);
onMounted(async () => {
	customerList.value = await getCustomerNames()
	serviceList.value = await getAllServices()
	console.log(serviceList.value)
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
		customerInfo.value = { id: '', name, contact_no: '', email: '', address: '' };
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
const date_received = ref(new Date);
const items = ref<JobItem[]>([{
	jo_number: '',
	item_id: '',
	description: '',
	height: 0,
	width: 0,
	size_unit: '',
	paper_size: '',
	quantity: 0,
	job_status: '',
	due_date: '',
	discount: 0,
	unit_price: 0,
	subtotal: 0,
	total_claimed: 0,
	remaining_on_hand: 0,
	service_name: '',
	extra_service_name: '',
	extra_service_price: 0,
}]);
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-xl font-semibold">Add Job Order</h1>
			<h2>Inserts job order information into the database upon saving.</h2>
		</div>
		<Button label="Save">
			<template #icon>
				<Save />
			</template>
		</Button>
	</section>
	<section class="mt-4 flex flex-col">
		<label class="mb-1 text-slate-700 font-medium">Customer Name</label>
		<Select v-model="customerName" fluid editable :options="customerList" placeholder="Select or input a customer"
			class="w-full md:w-56" />
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
			<InputNumber v-model="jo_number" placeholder="JO Number" :useGrouping="false" fluid />
		</div>
		<div class="flex flex-col">
			<label class="mb-1 text-slate-700 font-medium">Date Received</label>
			<DatePicker v-model="date_received" :maxDate="new Date" showTime hourFormat="12" />
		</div>
	</section>
	<section class="mt-4 rounded-md border border-slate-300 overflow-hidden">
		<JobItemsTable v-model:items="items" :jo_number="jo_number" :service_list="serviceList" />
	</section>
	<section class="mt-4">
		<p class="text-lg font-medium text-slate-700">Payments</p>
	</section>
	<section class="mt-4">
		<p class="text-lg font-medium text-slate-700">Claiming History</p>
	</section>
</template>