<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { JobOrder, JobItem } from '@/types/jobOrder'
import { getJobOrder } from '@/api/jobOrders'
import { formatDate, formatCurrency, getJobStatusColor, getPaymentStatusColor } from '@/utils/formatters'
import EditJobItemForm from '@/components/EditJobItemForm.vue'

const route = useRoute()
const router = useRouter()
const jobOrder = ref<JobOrder>()
const loading = ref(true)
const isEditJobItemOpen = ref(false)
const selectedJobItem = ref<JobItem | null>(null)

onMounted(async () => {
    loading.value = true
    jobOrder.value = await getJobOrder(Number(route.params.jo_number))
    loading.value = false
})

const balance = computed(() => (jobOrder.value ? jobOrder.value.total_due - jobOrder.value.total_paid : 0))

const printJobOrder = () => {
    const resolved = router.resolve(`/job-orders/print/${jobOrder.value?.jo_number}`)
    window.open(resolved.href, '_blank')
}

const openEditJobItem = (item: JobItem) => {
    selectedJobItem.value = item
    isEditJobItemOpen.value = true
}
</script>

<template>
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
        <EditJobItemForm v-model:isOpen="isEditJobItemOpen" :job-item="selectedJobItem" />
        <section class="bg-default border border-default rounded-md">
            <div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
                <div class="flex items-center gap-2">
                    <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                    <h2 class="text-highlighted font-semibold">Job Items</h2>
                </div>
                <UButton icon="i-lucide-plus" label="Add Item" variant="outline" />
            </div>
            <div class="overflow-hidden">
                <table class="w-full text-base">
                    <thead class="bg-elevated">
                        <tr class="text-left text-sm text-muted uppercase">
                            <th class="p-3">Item</th>
                            <th class="p-3">Service</th>
                            <th class="p-3">Size</th>
                            <th class="p-3">Qty</th>
                            <th class="p-3">Unit Price</th>
                            <th class="p-3">Subtotal</th>
                            <th class="p-3">Due Date</th>
                            <th class="p-3">Claimed</th>
                            <th class="p-3">Status</th>
                            <th class="p-3"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="item in jobOrder.job_items" :key="item.item_id">
                            <tr class="border-t border-default odd:bg-elevated/20 align-middle">
                                <td class="p-3 text-highlighted">{{ item.item_id }}</td>
                                <td class="p-3 text-highlighted">
                                    <UTooltip v-if="item.description || item.notes" :text="[
                                        item.description ? `Description: ${item.description}` : '',
                                        item.notes ? `Notes: ${item.notes}` : ''
                                    ].filter(Boolean).join('\n')">
                                        <div class="flex items-center gap-2 whitespace-nowrap cursor-help">
                                            <span>
                                                {{ item.service_name_snapshot }}

                                                <span v-if="item.service_option_name_snapshot" class="text-muted">
                                                    — {{ item.service_option_name_snapshot }}
                                                </span>
                                            </span>

                                            <span v-for="extra_item in item.extras" :key="extra_item.id"
                                                class="text-muted">
                                                — {{ extra_item.name_snapshot }} ({{ extra_item.quantity }}×)
                                            </span>
                                        </div>
                                    </UTooltip>

                                    <div v-else class="flex items-center gap-2 whitespace-nowrap">
                                        <span>
                                            {{ item.service_name_snapshot }}

                                            <span v-if="item.service_option_name_snapshot" class="text-muted">
                                                — {{ item.service_option_name_snapshot }}
                                            </span>
                                        </span>

                                        <span v-for="extra_item in item.extras" :key="extra_item.id" class="text-muted">
                                            — {{ extra_item.name_snapshot }} ({{ extra_item.quantity }}×)
                                        </span>
                                    </div>
                                </td>
                                <td class="p-3 text-highlighted">
                                    {{ item.width && item.height ? `${item.width} × ${item.height} ${item.size_unit}` :
                                        '—' }}
                                </td>
                                <td class="p-3 text-highlighted">{{ item.quantity }} pc(s)</td>
                                <td class="p-3 text-highlighted">{{ formatCurrency(item.unit_price) }}</td>
                                <td class="p-3 font-semibold text-highlighted">
                                    <UTooltip v-if="item.extra_total > 0 || item.discount_amount > 0" :text="[
                                        item.extra_total > 0
                                            ? `Extra Charge: ${formatCurrency(item.extra_total)}`
                                            : '',
                                        item.discount_amount > 0
                                            ? `Discount: −${formatCurrency(item.discount_amount)}`
                                            : ''
                                    ].filter(Boolean).join('\n')">
                                        <span class="cursor-help">
                                            {{ formatCurrency(item.subtotal) }}
                                        </span>
                                    </UTooltip>

                                    <span v-else>
                                        {{ formatCurrency(item.subtotal) }}
                                    </span>
                                </td>
                                <td class="p-3 text-highlighted">{{ formatDate(item.due_date) }}</td>
                                <td class="p-3 text-highlighted">
                                    {{ item.total_claimed }} / {{ item.quantity }}
                                </td>
                                <td class="p-3">
                                    <UBadge variant="outline" :color="getJobStatusColor(item.job_status)"
                                        class="font-semibold">{{ item.job_status }}
                                    </UBadge>
                                </td>
                                <td class="p-3">
                                    <UButton variant="outline" icon="i-lucide-pen-square" @click="openEditJobItem(item)" />
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </section>

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
</template>