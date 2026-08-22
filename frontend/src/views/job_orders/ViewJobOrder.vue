<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// Type imports
import type { JobOrder, JobItem, JobItemCreate, JobItemTableRow, JobItemUpdate } from '@/types/jobOrder'
import type { Service } from '@/types/service'
// API call imports
import { getJobOrder, createJobItem, updateJobItem } from '@/api/jobOrders'
import { getAllServices } from '@/api/services'
// Component imports
import JobItemTable from '@/components/JobItemTable.vue'
import AddJobItemForm from '@/components/job-item-form/AddJobItemForm.vue'
import EditJobItemForm from '@/components/job-item-form/EditJobItemForm.vue'
import OrderSummary from '@/components/OrderSummary.vue'
import PaymentTable from '@/components/PaymentTable.vue'
import PaymentForm from '@/components/PaymentForm.vue'

import { formatDate } from '@/utils/formatters'

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
const balance = computed(() => (jobOrder.value ? jobOrder.value.total_due - jobOrder.value.total_paid : 0))
const printJobOrder = () => {
    const resolved = router.resolve(`/job-orders/print/${jobOrder.value?.jo_number}`)
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
    catch (error) {
        console.error('Failed to create job item:', error)
        toast.add({
            title: 'Saving data failed.',
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const saveUpdatedItemToDb = async (payload: { id: string; changes: JobItemUpdate }) => {
    try {
        await updateJobItem(payload.changes, payload.id)
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
</script>

<template>
    <AddJobItemForm v-model:is-open="isAddFormOpen" :jo-number="jobOrder?.jo_number" :current-item-ids="currentItemIds"
        @save="saveNewItemToDb" />
    <EditJobItemForm v-model:is-open="isEditFormOpen" :job-item="selectedJobItem" v-if="selectedJobItem"
        @submit="saveUpdatedItemToDb" />
    <PaymentForm :balance="balance" :is-open="isPaymentFormOpen" />
    <Transition name="fade" mode="out-in">
        <div v-if="loading" class="flex items-center justify-center py-24">
            <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-muted" />
        </div>

        <div v-else-if="jobOrder" class="m-6 flex flex-col gap-6">
            <!-- Back + Title -->
            <div class="flex items-center justify-between">
                <UButton icon="i-lucide-arrow-left" label="Back to Job Orders" color="neutral" variant="outline"
                    to="/job-orders" />
                <UButton icon="i-lucide-printer" label="Print Job Order" variant="subtle" @click="printJobOrder" />
            </div>

            <!-- Order Summary With Customer Info -->
            <OrderSummary :job-order="jobOrder" :balance="balance" />
            
            <!-- Job Items -->
            <JobItemTable :job-items="jobOrder.job_items" :can-call-api="true" :jo-number="jobOrder.jo_number"
                @added="fetchJobOrder" @updated="fetchJobOrder" @open-form="openAddItemForm">
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
                </template>
            </JobItemTable>

            <!-- Payments -->
            <PaymentTable :balance="balance" :payments="jobOrder.payments" @open-form="openAddPaymentForm" />

            <!-- Claiming History -->
            <section class="bg-default border border-default rounded-md">
                <div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
                    <div class="flex items-center gap-2">
                        <UIcon name="i-lucide-scroll-text"
                            class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                        <h2 class="text-highlighted font-semibold">Claiming History</h2>
                    </div>
                    <UButton icon="i-lucide-plus" label="Add Claim" variant="outline" />
                </div>
                <div v-if="jobOrder.claiming_history.length">
                    <table class="w-full text-base">
                        <thead class="bg-elevated">
                            <tr class="text-left text-sm text-muted uppercase">
                                <th class="p-3">Date Claimed</th>
                                <th class="p-3">Name</th>
                                <th class="p-3">Item Claimed</th>
                                <th class="p-3">Pieces Claimed</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="claim in jobOrder.claiming_history" :key="claim.claimed_item_id"
                                class="odd:bg-elevated/20">
                                <td class="p-3 text-highlighted">{{ formatDate(claim.date_claimed) }}</td>
                                <td class="p-3 text-highlighted">{{ claim.name }}</td>
                                <td class="p-3 text-highlighted">{{ claim.claimed_item_id }}</td>
                                <td class="p-3 text-highlighted">{{ claim.pcs_claimed }} pc(s)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted text-base p-4 text-center">No claims recorded yet.</p>
            </section>
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