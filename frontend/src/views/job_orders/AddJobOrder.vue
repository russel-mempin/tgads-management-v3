<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
// Type imports
import type { JobItemTableRow, JobItemCreate, JobItemExtra, JobItem } from '@/types/jobOrder';
import type { Customer } from '@/types/customer';
import type { Service, Extra } from '@/types/service';
// API call imports
import { getCustomerNames, getCustomerInfo } from '@/api/customers'
import { getAllServices, getAllExtras } from '@/api/services';
import { getUnitPrice } from '@/api/jobOrders';
// Component imports
import JobItemTable from '@/components/JobItemTable.vue';
import { nowForInput } from '@/utils/formatters';

// Data Variables
const joNumber = ref(0)
const jobItems = ref<JobItemTableRow[]>([])
const dateReceived = ref(nowForInput())
const customerInfo = ref<Customer>({
	name: '',
	contact_no: '',
	email: '',
	address: '',
	id: '',
})

// UI Variables
const isWalkIn = ref(false)
const customerNameToSearch = ref('')
const showCustomerSuggestions = ref(false)
const customerList = ref<string[]>([])
const isNewCustomer = ref(false)
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const isAddFormOpen = ref(false)
const selectedJobItem = ref<JobItem | null>(null)

// Data Functions
onMounted(async () => {
	customerList.value = await getCustomerNames()
	serviceList.value = await getAllServices()
	extraList.value = await getAllExtras()
})
watch(customerNameToSearch, async (name) => {
	if (!name) {
		customerInfo.value = { name: '', contact_no: '', email: '', address: '', id: '' }
		return
	}
	const exists = customerList.value.some(
		(c) => c.toLowerCase() === name.toLowerCase()
	)
	if (exists) {
		isNewCustomer.value = false
		const data = await getCustomerInfo(name)
		if (!data) return
		customerInfo.value = {
			...data,
			address: data.address?.trim() || 'N/A',
			contact_no: data.contact_no?.trim() || 'N/A',
			email: data.email?.trim() || 'N/A',
		}
	} else {
		isNewCustomer.value = true
		customerInfo.value = { name: name, contact_no: '', email: '', address: '' }
	}
})

// UI Functions
const handleBlur = () => {
	setTimeout(() => {
		showCustomerSuggestions.value = false
	}, 150)
}
const filteredCustomers = computed(() => {
	if (!customerNameToSearch.value) return []
	const q = customerNameToSearch.value.toLowerCase()
	return customerList.value.filter(c => c.toLowerCase().includes(q)).slice(0, 8)
})
const selectCustomerToSearch = (name: string) => {
	customerNameToSearch.value = name
	showCustomerSuggestions.value = false
}
const currentItemIds = computed(() =>
	jobItems.value?.map(item => item.item_id) ?? []
)
const openAddItemForm = () => {
	isAddFormOpen.value = true
}
const openEditItemForm = (item: JobItemTableRow) => {
	const service = serviceList.value.find(
		service => service.name === item.service_name_snapshot
	)
	if (!service?.id) {
		console.error(`Service not found: ${item.service_name_snapshot}`)
		return
	}
	const option = service.options.find(
		option => option.name === item.service_option_name_snapshot
	)
	if (!option?.id) {
		console.error(
			`Option not found: ${item.service_option_name_snapshot}`
		)
		return
	}
	selectedJobItem.value = {
		...item,
		id: item.item_id,
		service_id: service.id,
		service_option_id: option.id,
		service_abbreviation_snapshot: service.abbreviation
	}
	isAddFormOpen.value = true
}
const buildJobItem = async (item: JobItemCreate): Promise<JobItemTableRow> => {
	const service = serviceList.value.find(s => s.id === item.service_id)
	const option = service?.options.find(o => o.id === item.service_option_id)
	const pricingData = await getUnitPrice({
		height: item.height ?? 0,
		width: item.width ?? 0,
		service_id: item.service_id,
		option_id: item.service_option_id,
		size_unit: item.size_unit!,
		quantity: item.quantity
	})
	const extras: JobItemExtra[] = item.extras.map(e => {
		const extra = extraList.value.find(x => x.id === e.extra_service_id)

		return {
			extra_service_id: e.extra_service_id,
			quantity: e.quantity,
			name_snapshot: extra?.name ?? 'Unknown Extra',
			price_snapshot: extra?.price ?? 0
		}
	})
	const extraTotal = extras.reduce(
		(sum, e) => sum + e.price_snapshot * e.quantity,
		0
	)
	const extraChargeTotal = item.extra_charge * item.quantity
	const subtotal =
		(pricingData.unit_price * item.quantity) +
		extraTotal +
		extraChargeTotal -
		item.discount_amount

	return {
		...item,
		unit_price: pricingData.unit_price,
		subtotal,
		service_name_snapshot: service?.name ?? '-',
		service_option_name_snapshot: option?.name ?? '-',
		total_claimed: 0,
		remaining_on_hand: item.quantity,
		extras
	}
}
const saveJobItem = async (item: JobItemCreate) => {
	const converted = await buildJobItem(item)
	if (!selectedJobItem.value) {
		jobItems.value.push(converted)
	}
	else {
		const index = jobItems.value.findIndex(
            jobItem => jobItem.item_id === selectedJobItem.value?.item_id
        )
		if (index !== -1) {
            jobItems.value[index] = converted
        }	
	}
}
const deleteJobItem = (index: number) => {
	if (index !== -1) {
		jobItems.value.splice(index, 1)
	}
}
</script>

<template>
	<AddJobItemForm v-model:is-open="isAddFormOpen" :jo-number="joNumber" :current-item-ids="currentItemIds"
		:editing-item="selectedJobItem" @save="saveJobItem" />
	<!-- Page Header -->
	<div class="m-8 shrink-0">
		<div class="flex items-start justify-between">
			<div>
				<p class="text-xs font-semibold uppercase tracking-widest text-primary mb-1">New Entry</p>
				<h1 class="text-2xl font-bold text-highlighted">Add Job Order</h1>
				<p class="text-sm text-muted mt-1">
					Fields marked <span class="text-error font-semibold">*</span> are required.
				</p>
			</div>
			<div class="flex items-center gap-3 bg-elevated border border-default rounded-md px-4 py-3 mt-1">
				<div>
					<p class="text-base font-semibold text-highlighted">Walk-in Customer</p>
					<p class="text-xs text-muted">No customer record needed</p>
				</div>
				<USwitch v-model="isWalkIn" size="lg" />
			</div>
		</div>
	</div>

	<!-- Order Information -->
	<div class="bg-default border border-default rounded-md p-6 m-8">
		<div class="flex items-center gap-2 mb-6">
			<UIcon name="i-lucide-hash" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
			<h2 class="font-semibold text-highlighted">Order Information</h2>
		</div>
		<div class="grid grid-cols-2 gap-6">
			<UFormField label="Job Order No." required>
				<UInput v-model="joNumber" type="number" placeholder="e.g. 19291" size="lg" class="w-full"
					:disabled="jobItems.length > 0" :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''"
					@focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
			</UFormField>
			<UFormField label="Date Received" required>
				<UInput v-model="dateReceived" type="datetime-local" size="lg" class="w-full" />
			</UFormField>
		</div>
	</div>

	<!-- Customer Selector -->
	<Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2"
		enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
		leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
		<div v-if="!isWalkIn" class="bg-default border border-default rounded-md p-6 m-8">
			<div class="flex items-center gap-2 mb-8">
				<UIcon name="i-lucide-user" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<h2 class="font-semibold text-highlighted">Customer</h2>
			</div>
			<UFormField label="Name" hint="Type to search existing customers, or enter a new name." required>
				<div class="relative">
					<UInput v-model="customerNameToSearch" placeholder="Search or enter customer name" size="lg"
						class="w-full" @focus="showCustomerSuggestions = true" @blur="handleBlur" />
					<div v-if="showCustomerSuggestions && filteredCustomers.length"
						class="absolute z-20 mt-1 w-full bg-default border border-default rounded-md shadow-lg max-h-48 overflow-y-auto">
						<button v-for="name in filteredCustomers" :key="name" type="button"
							class="w-full text-left px-3 py-2 hover:bg-elevated text-sm"
							@mousedown="selectCustomerToSearch(name)">
							{{ name }}
						</button>
					</div>
				</div>
			</UFormField>
			<div class="mt-6 grid grid-cols-3 gap-6">
				<UFormField label="Contact Number">
					<UInput v-model="customerInfo.contact_no" placeholder="09XX-XXX-XXXX" size="lg" class="w-full"
						:disabled="!isNewCustomer" />
				</UFormField>
				<UFormField label="Email">
					<UInput v-model="customerInfo.email" placeholder="teamgraphicads@yahoo.com" size="lg" class="w-full"
						:disabled="!isNewCustomer"
						:hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
				</UFormField>
				<UFormField label="Address">
					<UInput v-model="customerInfo.address" :items="customerList" placeholder="134 Luzon Ave." size="lg"
						class="w-full" :disabled="!isNewCustomer"
						:hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
				</UFormField>
			</div>
		</div>
	</Transition>

	<!-- Job Items -->
	<div class="m-8">
		<JobItemTable :job-items="jobItems" :jo-number="joNumber" @open-form="openAddItemForm">
			<template #actions="{ item, index }">
				<UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
				<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" @click="deleteJobItem(index)" />
			</template>
		</JobItemTable>
	</div>
</template>