<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// Type imports
import type { JobOrder, JobItem, JobItemCreate } from '@/types/jobOrder'
// API call imports
import { getJobOrder, createJobItem, updateJobItem } from '@/api/jobOrders'
// Component imports
import JobItemTable from '@/components/JobItemTable.vue'
import AddJobItemForm from '@/components/job-item-form/AddJobItemForm.vue'
import EditJobItemForm from '@/components/job-item-form/EditJobItemForm.vue'
import { formatDate, formatCurrency, getJobStatusColor, getPaymentStatusColor } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// Data variables
const jobOrder = ref<JobOrder>()
const editingJobItem = ref<JobItem>()

// UI variables
const loading = ref(true)
const isAddFormOpen = ref(false)
const isEditFormOpen = ref(false)
const isAdding = ref(false)
const isUpdating = ref(false)
const currentItemIds = computed(() =>
    jobOrder.value?.job_items.map(item => item.item_id) ?? []
)

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
onMounted(fetchJobOrder)

// UI functions
const balance = computed(() => (jobOrder.value ? jobOrder.value.total_due - jobOrder.value.total_paid : 0))
const printJobOrder = () => {
    const resolved = router.resolve(`/job-orders/print/${jobOrder.value?.jo_number}`)
    window.open(resolved.href, '_blank')
}
const openAddItemForm = () => {
    isAddFormOpen.value = true
}
const openEditItemForm = (item: JobItem) => {
    isEditFormOpen.value = true
    editingJobItem.value = item
}
const saveNewItemToDb = async (item: JobItemCreate) => {
    if (!jobOrder.value) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createJobItem(item, jobOrder.value.id)
        await fetchJobOrder()
        toast.add({
            title: 'Saved successfully',
            color: 'success',
        })
    }
    catch (error) {
        console.error('Failed to create job item:', error)
        toast.add({
            title: 'Save failed',
            description: 'Something went wrong while saving the job item.',
            color: 'error',
        })
    }
}
const saveUpdatedItemToDb = async (payload: { jobItemId: string, changes: Partial<JobItem> }) => {
    if (!payload.jobItemId) return
    if (isUpdating.value) return
    isUpdating.value = true
    try {
        await updateJobItem(payload.changes, payload.jobItemId)
        toast.add({
            title: 'Job item updated',
            color: 'success',
        })
        isEditFormOpen.value = false
        await fetchJobOrder()
    }
    catch (error) {
        console.error('Failed to update job item:', error)
        toast.add({
            title: 'Save failed',
            description: 'Something went wrong while saving the job item.',
            color: 'error',
        })
    }
    finally {
        isUpdating.value = false
    }
}
</script>

<template>
    <AddJobItemForm v-model:is-open="isAddFormOpen" :jo-number="jobOrder?.jo_number" :current-item-ids="currentItemIds"
        @save="saveNewItemToDb" />
    <EditJobItemForm v-if="editingJobItem" v-model:is-open="isEditFormOpen" :job-item="editingJobItem"
        @update="saveUpdatedItemToDb" />
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

            <!-- Order Summary -->
            <div class="flex items-center gap-6">
                <h1 class="text-2xl font-semibold text-highlighted">Job Order #{{ jobOrder.jo_number }}</h1>
                <div class="flex gap-2">
                    <UBadge :color="getPaymentStatusColor(jobOrder.payment_status)" variant="subtle" size="lg"
                        class="font-semibold">{{
                            jobOrder.payment_status }}</UBadge>
                    <UBadge :color="getJobStatusColor(jobOrder.overall_job_status)" variant="subtle" size="lg"
                        class="font-semibold">{{
                            jobOrder.overall_job_status }}</UBadge>
                </div>
            </div>

            <!-- Summary -->
            <div class="grid grid-cols-3 gap-6">
                <div class="border border-default bg-default rounded-md p-4">
                    <p class="text-sm text-muted uppercase font-semibold">Total Due</p>
                    <p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_due) }}</p>
                </div>
                <div class="border border-default bg-default rounded-md p-4">
                    <p class="text-sm text-muted uppercase font-semibold">Total Paid</p>
                    <p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_paid) }}</p>
                </div>
                <div class="border border-default bg-default rounded-md p-4"
                    :class="balance > 0 ? 'border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30' : 'border-default bg-default'">
                    <p class="text-sm uppercase font-semibold"
                        :class="balance > 0 ? 'text-red-700 dark:text-red-400' : 'text-muted'">Balance</p>
                    <p class="text-2xl font-bold mt-1"
                        :class="balance > 0 ? 'text-red-700 dark:text-red-400' : 'text-highlighted'">
                        {{ formatCurrency(balance) }}
                    </p>
                </div>
            </div>

            <!-- Customer Information -->
            <section class="bg-default border border-default rounded-md">
                <div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
                    <div class="flex items-center gap-2">
                        <UIcon name="i-lucide-user" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                        <h2 class="text-highlighted font-semibold">Customer and Order Info</h2>
                    </div>
                </div>
                <div class="m-6 grid grid-cols-3 gap-6">
                    <div>
                        <p class="text-sm text-muted uppercase">Name</p>
                        <p class="text-base text-highlighted">{{ jobOrder.customer_name ?? 'Walk-in' }}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted uppercase">Contact No.</p>
                        <p class="text-base text-highlighted">{{ jobOrder.customer_contact_no ?? '—' }}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted uppercase">Email</p>
                        <p class="text-base text-highlighted">{{ jobOrder.customer_email ?? '—' }}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted uppercase">Date Received</p>
                        <p class="text-base text-highlighted">{{ formatDate(jobOrder.date_received) }}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted uppercase">Last Updated</p>
                        <p class="text-base text-highlighted">{{ formatDate(jobOrder.updated_at) }}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted uppercase">Last Update By</p>
                        <p class="text-base text-highlighted">{{ jobOrder.updated_by_name }}</p>
                    </div>
                </div>
            </section>

            <!-- Job Items -->
            <JobItemTable :job-items="jobOrder.job_items" :jo-number="jobOrder.jo_number" @added="fetchJobOrder"
                @updated="fetchJobOrder" @open-form="openAddItemForm">
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
                </template>
            </JobItemTable>

            <!-- Payments -->
            <section class="bg-default border border-default rounded-md">
                <div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
                    <div class="flex items-center gap-2">
                        <UIcon name="i-lucide-philippine-peso"
                            class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                        <h2 class="text-highlighted font-semibold">Payments</h2>
                    </div>
                    <UButton icon="i-lucide-plus" label="Add Payment" variant="outline" />
                </div>
                <div v-if="jobOrder.payments.length">
                    <table class="w-full text-base">
                        <thead class="bg-elevated">
                            <tr class="text-left text-sm text-muted uppercase">
                                <th class="p-3">Date Received</th>
                                <th class="p-3">Reference #</th>
                                <th class="p-3">Method</th>
                                <th class="p-3">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="payment in jobOrder.payments" :key="payment.reference_number"
                                class="border-t border-default odd:bg-elevated/20">
                                <td class="p-3 text-highlighted">{{ formatDate(payment.date_received) }}</td>
                                <td class="p-3 text-highlighted">{{ payment.reference_number }}</td>
                                <td class="p-3 text-highlighted">{{ payment.account_name_snapshot }}</td>
                                <td class="p-3 font-semibold text-highlighted">{{ formatCurrency(payment.amount) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted text-base p-4 text-center">No payments recorded
                    yet.
                </p>
            </section>

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