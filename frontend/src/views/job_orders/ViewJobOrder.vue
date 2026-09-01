<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios';
// Type imports
import type { JobOrder, JobItem, JobItemCreate, JobItemTableRow, JobItemUpdate, Payment, ClaimingHistory } from '@/types/jobOrder'
import type { Service } from '@/types/service'
// API call imports
import { getJobOrder, createJobItem, updateJobItem, createPayment, createClaim } from '@/api/jobOrders'
import { getAllServices } from '@/api/services'
// Component imports
import JobItemTable from '@/components/JobItemTable.vue'
import AddJobItemForm from '@/components/job-item-form/AddJobItemForm.vue'
import EditJobItemForm from '@/components/job-item-form/EditJobItemForm.vue'
import OrderSummary from '@/components/OrderSummary.vue'
import PaymentTable from '@/components/PaymentTable.vue'
import PaymentForm from '@/components/PaymentForm.vue'
import ClaimTable from '@/components/ClaimTable.vue'
import { useJobOrderTotals } from '@/composables/jobOrderTotals'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// Data variables
const jobOrder = ref<JobOrder>()

// UI variables
const loading = ref(true)
const isAddFormOpen = ref(false)
const isEditFormOpen = ref(false)
const currentItemIds = computed(() =>
    jobOrder.value?.job_items.map(item => item.item_id) ?? []
)
const selectedJobItem = ref<JobItem | null>(null)
const serviceList = ref<Service[]>([])
const isPaymentFormOpen = ref(false)
const isClaimFormOpen = ref(false)

const joNumber = computed(() => jobOrder.value?.jo_number ?? 0)
const jobItems = computed(() => jobOrder.value?.job_items ?? [])
const payments = computed(() => jobOrder.value?.payments ?? [])
const claimingHistory = computed(() => jobOrder.value?.claiming_history ?? [])
const { claimableItemIds, balance } = useJobOrderTotals(joNumber, jobItems, payments, claimingHistory)
const isCancelled = computed(() => jobOrder.value?.overall_job_status === 'Cancelled')

// Data functions 
const fetchJobOrder = async () => {
    loading.value = true
    try {
        const jobOrderId = route.params.job_order_id
        if (typeof jobOrderId !== 'string') {
            throw new Error('Invalid job order ID')
        }
        jobOrder.value = await getJobOrder(jobOrderId)
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    fetchJobOrder()
    serviceList.value = await getAllServices()
})

// UI functions
const printJobOrder = () => {
    const resolved = router.resolve(`/job-orders/print/${route.params.job_order_id}`)
    window.open(resolved.href, '_blank')
}
const openAddItemForm = () => {
    isAddFormOpen.value = true
}
const openEditItemForm = (item: JobItemTableRow) => {
    const service = serviceList.value.find(
        service => service.name === item.service_name_snapshot
    )
    if (!item.id) {
        console.error(`Job item has no ID: ${item.item_id}`)
        return
    }
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
        id: item.id,
        service_id: service.id,
        service_option_id: option.id,
        service_abbreviation_snapshot: service.abbreviation
    }
    isEditFormOpen.value = true
}
const saveNewItemToDb = async (item: JobItemCreate) => {
    if (!jobOrder.value) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createJobItem(item, jobOrder.value.id)
        toast.add({
            title: 'Job Item Added.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchJobOrder()
    }
    catch (error: unknown) {
        console.error('Failed to create payment:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to create payment.'
        }

        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const saveUpdatedItemToDb = async (payload: { id: string; changes: JobItemUpdate }) => {
    if (!jobOrder.value) return
    try {
        await updateJobItem(payload.changes, jobOrder.value.id, payload.id)
        toast.add({
            title: 'Job Item Updated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
    }
    catch (error) {
        console.error('Failed to update job item', error)
        toast.add({
            title: 'Updating data failed.',
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
    finally {
        isEditFormOpen.value = false
        fetchJobOrder()
    }
}
const openAddPaymentForm = () => {
    isPaymentFormOpen.value = true
}
const saveNewPaymentToDb = async (item: Payment) => {
    if (!jobOrder.value) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createPayment(item, jobOrder.value.id)
        toast.add({
            title: 'Payment data saved.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchJobOrder()
    }
    catch (error: unknown) {
        console.error('Failed to create payment:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to create payment.'
        }

        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const openAddClaimForm = () => {
    isClaimFormOpen.value = true
}
const saveNewClaimToDb = async (item: ClaimingHistory) => {
    if (!jobOrder.value) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createClaim(item, jobOrder.value.id)
        toast.add({
            title: 'Claim data saved.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchJobOrder()
    }
    catch (error: unknown) {
        console.error('Failed to create payment:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to create payment.'
        }

        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
</script>

<template>
    <AddJobItemForm v-model:is-open="isAddFormOpen" :jo-number="jobOrder?.jo_number" :current-item-ids="currentItemIds"
        @save="saveNewItemToDb" />
    <EditJobItemForm v-model:is-open="isEditFormOpen" :job-item="selectedJobItem" v-if="selectedJobItem"
        @submit="saveUpdatedItemToDb" />
    <PaymentForm :balance="balance" :is-open="isPaymentFormOpen" @save="saveNewPaymentToDb" />
    <ClaimForm :claimable-item-ids="claimableItemIds" v-model:is-open="isClaimFormOpen" @save="saveNewClaimToDb" />
    <Transition name="fade" mode="out-in">
        <div v-if="loading" class="flex items-center justify-center py-24">
            <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-muted" />
        </div>

        <div v-else-if="jobOrder" class="m-6 flex flex-col gap-6">
            <!-- Back + Title -->
            <div class="flex items-center justify-between">
                <UButton icon="i-lucide-arrow-left" label="Back to Job Orders" color="neutral" variant="outline"
                    to="/job-orders" />
                <div class="flex gap-4">
                    <UButton icon="i-lucide-printer-x" label="Void Job Order" color="warning" variant="subtle" @click="printJobOrder" />
                    <UButton icon="i-lucide-printer" label="Print Job Order" variant="subtle" @click="printJobOrder" />
                </div>
            </div>

            <!-- Order Summary With Customer Info -->
            <OrderSummary :job-order="jobOrder" />

            <!-- Job Items -->
            <JobItemTable :job-items="jobOrder.job_items" :can-call-api="true" :jo-number="jobOrder.jo_number"
                @added="fetchJobOrder" @updated="fetchJobOrder">
                <template #header-actions>
                    <UTooltip :text="!joNumber ? 'A valid job order number is required' : 'Add an item'">
                        <span>
                            <UButton @click="openAddItemForm" :disabled="!joNumber || joNumber <= 0"
                                icon="i-lucide-plus" label="Add Item" variant="outline" />
                        </span>
                    </UTooltip>
                </template>
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
                </template>
            </JobItemTable>

            <!-- Payments -->
            <PaymentTable :balance="balance" :payments="jobOrder.payments" :is-job-cancelled="isCancelled"
                @open-form="openAddPaymentForm" />

            <!-- Claiming History -->
            <ClaimTable :claiming-history="jobOrder.claiming_history" :job-items="jobOrder.job_items"
                :claimable-items="claimableItemIds" :is-job-cancelled="isCancelled" @open-form="openAddClaimForm">
                <template #header-actions>
                    <UTooltip :text="claimableItemIds.length === 0 ? 'No claimable items.' : 'Add an item'">
                        <span>
                            <UButton @click="openAddClaimForm" :disabled="claimableItemIds.length === 0"
                                icon="i-lucide-plus" label="Add Item" variant="outline" />
                        </span>
                    </UTooltip>
                </template>
            </ClaimTable>
        </div>
    </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>