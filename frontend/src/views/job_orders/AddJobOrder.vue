<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router';
// Type imports
import type { JobItemTableRow, JobItemCreate, JobItem, Payment, ClaimingHistory } from '@/types/jobOrder';
import type { Service, Extra } from '@/types/service';
// API call imports
import { getAllServices, getAllExtras } from '@/api/services';
import { createJobOrder, getUnitPrice } from '@/api/jobOrders';
// Component imports
import JobItemTable from '@/components/JobItemTable.vue';
import PaymentTable from '@/components/PaymentTable.vue';
import AddJobOrderHeader from '@/components/AddJobOrderHeader.vue';
import OrderInfoInput from '@/components/OrderInfoInput.vue';
import CustomerSelector from '@/components/CustomerSelector.vue';
import JobOrderFooter from '@/components/JobOrderFooter.vue';
import ClaimForm from '@/components/ClaimForm.vue';
import { inputToUtc, nowForInput } from '@/utils/formatters';
import { useJobOrderTotals } from '@/composables/jobOrderTotals';
import { useCustomerSearch } from '@/composables/customerSearch';
import { useJobItemBuilder } from '@/composables/jobItemBuilder';

const toast = useToast()
const router = useRouter()

// Data Variables
const joNumber = ref(0)
const jobItems = ref<JobItemTableRow[]>([])
const dateReceived = ref(nowForInput())
const payments = ref<Payment[]>([])
const claimingHistory = ref<ClaimingHistory[]>([])

// Data Functions
onMounted(async () => {
	serviceList.value = await getAllServices()
	extraList.value = await getAllExtras()
})

// UI Variables
const isWalkIn = ref(false)
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const isItemFormOpen = ref(false)
const selectedIndex = ref<number | null>(null)
const selectedJobItem = ref<JobItem | null>(null)
const isPaymentFormOpen = ref(false)
const selectedPayment = ref<Payment | null>(null)
const isClaimFormOpen = ref(false)
const selectedClaim = ref<ClaimingHistory | null>(null)

const { totalDue, totalPaid, balance, hasJobItems, canSave, getTotalClaimed, claimableItemIds } =
	useJobOrderTotals(joNumber, jobItems, payments, claimingHistory)
const {
	customerInfo,
	customerNameToSearch,
	showCustomerSuggestions,
	customerList,
	isNewCustomer,
	filteredCustomers,
	handleBlur,
	selectCustomerToSearch,
} = useCustomerSearch()
const { buildJobItem, resolveServiceId, resolveOptionId } = useJobItemBuilder(serviceList, extraList, getUnitPrice)



// UI Functions
const currentItemIds = computed(() =>
	jobItems.value?.map(item => item.item_id) ?? []
)
const openAddItemForm = () => {
	isItemFormOpen.value = true
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
	isItemFormOpen.value = true
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
const openAddPaymentForm = () => {
	isPaymentFormOpen.value = true
}
const openEditPaymentForm = (item: Payment, index: number) => {
	selectedPayment.value = item
	selectedIndex.value = index
	isPaymentFormOpen.value = true
}
const closePaymentForm = () => {
	isPaymentFormOpen.value = false
	selectedPayment.value = null
	selectedIndex.value = null
}
const savePayment = async (item: Payment) => {
	if (!selectedPayment.value) {
		payments.value.push(item)
	}
	else {
		if (selectedIndex.value !== null) {
			payments.value[selectedIndex.value] = item
		}
	}
}
const deletePayment = (index: number) => {
	if (index !== -1) {
		payments.value.splice(index, 1)
	}
}
const openAddClaimForm = () => {
	isClaimFormOpen.value = true
}
const openEditClaimForm = (item: ClaimingHistory, index: number) => {
	selectedClaim.value = item
	selectedIndex.value = index
	isClaimFormOpen.value = true
}
const deleteClaim = (index: number) => {
	if (index !== -1) {
		claimingHistory.value.splice(index, 1)
	}
}
const saveClaim = async (item: ClaimingHistory) => {
	if (!selectedPayment.value) {
		claimingHistory.value.push(item)
	}
	else {
		if (selectedIndex.value !== null) {
			claimingHistory.value[selectedIndex.value] = item
		}
	}
}

const saveToDb = async () => {
	const payload = {
		jo_number: joNumber.value,
		date_received: inputToUtc(dateReceived.value),
		...(isWalkIn.value ? {} : { customer_info: customerInfo.value }),
		job_items: jobItems.value.map(item => {
			const serviceId = resolveServiceId(item.service_name_snapshot)
			const serviceOptionId = resolveOptionId(
				item.service_name_snapshot,
				item.service_option_name_snapshot
			)
			if (!serviceId) {
				throw new Error(
					`Service "${item.service_name_snapshot}" could not be found.`
				)
			}
			if (!serviceOptionId) {
				throw new Error(
					`Service option "${item.service_option_name_snapshot}" could not be found.`
				)
			}
			return {
				item_id: item.item_id,
				description: item.description,
				quantity: item.quantity,
				job_status: item.job_status,
				due_date: item.due_date,
				notes: item.notes,
				extra_charge: item.extra_charge,
				discount_amount: item.discount_amount,
				width: item.width,
				height: item.height,
				size_unit: item.size_unit,
				service_id: serviceId,
				service_option_id: serviceOptionId,
				extras: item.extras.map(extra => ({
					extra_service_id: extra.extra_service_id,
					quantity: extra.quantity,
				})),
			}
		}),
		payments: payments.value,
		claiming_history: claimingHistory.value
	}

	try {
		await createJobOrder(payload)
		toast.add({
			title: 'Job Order Saved',
			description: `Job Order #${joNumber.value} was created successfully.`,
			color: 'success',
			icon: 'i-lucide-circle-check'
		})
		await router.push('/job-orders')
	}
	catch (error: any) {
		console.error(error)
		toast.add({
			title: 'Failed to Save',
			description: error.response?.data?.detail
				?? error.message
				?? 'An unexpected error occurred.',
			color: 'error',
			icon: 'i-lucide-circle-x'
		})
	}
}
</script>

<template>
	<AddJobItemForm v-model:is-open="isItemFormOpen" :jo-number="joNumber" :current-item-ids="currentItemIds"
		:editing-item="selectedJobItem" @save="saveJobItem" />
	<PaymentForm v-model:is-open="isPaymentFormOpen" :balance="balance" :editing-payment="selectedPayment"
		@save="savePayment" @close="closePaymentForm" />
	<ClaimForm v-model:is-open="isClaimFormOpen" :claimable-item-ids="claimableItemIds" :editing-claim="selectedClaim"
		@save="saveClaim" />

	<AddJobOrderHeader v-model:is-walk-in="isWalkIn" />

	<OrderInfoInput :has-job-items="hasJobItems" v-model:jo-number="joNumber" v-model:date-received="dateReceived" />

	<CustomerSelector :is-walk-in="isWalkIn" :has-job-items="hasJobItems"
		v-model:customer-name-to-search="customerNameToSearch" v-model:customer-info="customerInfo"
		v-model:show-customer-suggestions="showCustomerSuggestions" :customer-list="customerList"
		:is-new-customer="isNewCustomer" :filtered-customers="filteredCustomers" :handle-blur="handleBlur"
		:select-customer-to-search="selectCustomerToSearch" />

	<div class="flex flex-col gap-8 m-8">
		<JobItemTable :job-items="jobItems" :jo-number="joNumber" @open-form="openAddItemForm"
			:get-total-claimed="getTotalClaimed">
			<template #header-actions>
				<UTooltip :text="!joNumber ? 'A valid job order number is required' : 'Add an item'">
					<span>
						<UButton @click="openAddItemForm"
							:disabled="!joNumber || joNumber <= 0"
							icon="i-lucide-plus" label="Add Item" variant="outline" />
					</span>
				</UTooltip>
			</template>
			<template #actions="{ item, index }">
				<UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
				<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md"
					@click="deleteJobItem(index)" />
			</template>
		</JobItemTable>
		<PaymentTable :payments="payments" :balance="balance" @open-form="openAddPaymentForm">
			<template #actions="{ item, index }">
				<UButton icon="i-lucide-square-pen" variant="ghost" size="md"
					@click="openEditPaymentForm(item, index)" />
				<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md"
					@click="deletePayment(index)" />
			</template>
		</PaymentTable>
		<ClaimTable :claiming-history="claimingHistory" :job-items="jobItems" :claimable-items="claimableItemIds"
			@open-form="openAddClaimForm">
			<template #actions="{ item, index }">
				<UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditClaimForm(item, index)" />
				<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" @click="deleteClaim(index)" />
			</template>
		</ClaimTable>
	</div>
	<JobOrderFooter :total-due="totalDue" :total-paid="totalPaid" :balance="balance" :can-save="!canSave"
		@save="saveToDb" />
</template>