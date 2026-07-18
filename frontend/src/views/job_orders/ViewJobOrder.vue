<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { JobOrder } from '@/types/job_ordersTypes'
import { getJobOrder } from '@/api/job_orders'
import { formatDate, formatCurrency } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const jobOrder = ref<JobOrder>()
const loading = ref(true)

onMounted(async () => {
    loading.value = true
    jobOrder.value = await getJobOrder(Number(route.params.jo_number))
    loading.value = false
    console.log(jobOrder.value)
})

const balance = computed(() => (jobOrder.value ? jobOrder.value.total_due - jobOrder.value.total_paid : 0))

const paymentStatusColor = computed(() => ({
    'Fully Paid': 'success' as const,
    'Partial': 'warning' as const,
    'Unpaid': 'error' as const,
    'Credit': 'info' as const,
    'Refunded': 'neutral' as const,
    'Overcharged': 'warning' as const,
}[jobOrder.value?.payment_status ?? 'Unpaid']))

const jobStatusColor = computed(() => ({
    'Pending': 'warning' as const,
    'For Layout': 'info' as const,
    'For Approval': 'primary' as const,
    'For Printing': 'primary' as const,
    'For Pickup': 'success' as const,
    'Released': 'neutral' as const,
    'Cancelled': 'error' as const,
}[jobOrder.value?.overall_job_status ?? 'Pending']))

const printJobOrder = () => {
    const resolved = router.resolve(`/job-orders/print/${jobOrder.value?.jo_number}`)
    window.open(resolved.href, '_blank')
}
</script>

<template>
    <div v-if="loading" class="flex items-center justify-center py-24">
        <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-muted" />
    </div>

    <div v-else-if="jobOrder" class="flex flex-col gap-6">
        <!-- Back + Title -->
        <div class="flex items-center justify-between">
            <UButton icon="i-lucide-arrow-left" label="Back to Job Orders" color="neutral" variant="ghost"
                to="/job-orders" />
            <UButton icon="i-lucide-printer" label="Print Job Order" color="neutral" variant="outline" size="lg"
                @click="printJobOrder" />
        </div>

        <div class="flex items-center gap-4">
            <h1 class="text-2xl font-semibold text-highlighted">JO-{{ jobOrder.jo_number }}</h1>
            <UBadge :color="jobStatusColor" variant="soft" size="lg" class="font-semibold">{{
                jobOrder.overall_job_status }}</UBadge>
            <UBadge :color="paymentStatusColor" variant="soft" size="lg" class="font-semibold">{{
                jobOrder.payment_status }}</UBadge>
        </div>

        <!-- Summary -->
        <div class="grid grid-cols-3 gap-4">
            <div class="border border-default bg-default rounded-md p-4">
                <p class="text-sm text-muted uppercase font-semibold">Total Due</p>
                <p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_due) }}</p>
            </div>
            <div class="border border-default bg-default rounded-md p-4">
                <p class="text-sm text-muted uppercase font-semibold">Total Paid</p>
                <p class="text-2xl font-bold text-highlighted mt-1">{{ formatCurrency(jobOrder.total_paid) }}</p>
            </div>
            <div class="border rounded-md p-4"
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
        <section>
            <h2 class="text-lg font-semibold text-highlighted mb-3">Customer Information</h2>
            <div class="border border-default rounded-md p-4 grid grid-cols-3 gap-4">
                <div>
                    <p class="text-sm text-muted">Name</p>
                    <p class="text-base text-highlighted">{{ jobOrder.customer_name }}</p>
                </div>
                <div>
                    <p class="text-sm text-muted">Contact No.</p>
                    <p class="text-base text-highlighted">{{ jobOrder.customer_contact_no ?? '—' }}</p>
                </div>
                <div>
                    <p class="text-sm text-muted">Email</p>
                    <p class="text-base text-highlighted">{{ jobOrder.customer_email ?? '—' }}</p>
                </div>
                <div>
                    <p class="text-sm text-muted">Date Received</p>
                    <p class="text-base text-highlighted">{{ formatDate(jobOrder.date_received) }}</p>
                </div>
                <div>
                    <p class="text-sm text-muted">Last Updated</p>
                    <p class="text-base text-highlighted">{{ formatDate(jobOrder.updated_at) }}</p>
                </div>
            </div>
        </section>

        <!-- Job Items -->
        <section>
            <h2 class="text-lg font-semibold text-highlighted mb-3">Job Items ({{ jobOrder.job_items.length }})</h2>
            <div class="border border-default rounded-md overflow-hidden">
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
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="item in jobOrder.job_items" :key="item.item_id">
                            <tr class="border-t border-default odd:bg-elevated/20">
                                <td class="p-3 text-highlighted">{{ item.item_id }}</td>
                                <td class="p-3 text-highlighted">
                                    {{ item.service_name_snapshot }}
                                    <span class="text-muted" v-if="item.service_option_name_snapshot"> — {{
                                        item.service_option_name_snapshot }}</span>
                                    <span class="text-muted" v-if="item.extras.name_snapshot"> — {{ item.extras.name_snapshot }}</span>
                                </td>
                                <td class="p-3 text-highlighted">
                                    {{ item.width && item.height ? `${item.width} × ${item.height} ${item.size_unit}` :
                                        '—' }}
                                </td>
                                <td class="p-3 text-highlighted">{{ item.quantity }}</td>
                                <td class="p-3 text-highlighted">{{ formatCurrency(item.unit_price) }}</td>
                                <td class="p-3 font-semibold text-highlighted">{{ formatCurrency(item.subtotal) }}</td>
                                <td class="p-3 text-highlighted">{{ formatDate(item.due_date) }}</td>
                                <td class="p-3 text-highlighted">
                                    {{ item.total_claimed }} / {{ item.quantity }}
                                </td>
                                <td class="p-3">
                                    <UBadge variant="soft" color="neutral" class="font-semibold">{{ item.job_status }}
                                    </UBadge>
                                </td>
                            </tr>
                            <!-- Only rendered when there's something extra to show for this item -->
                            <tr v-if="item.description || item.notes || item.discount > 0 || item.extra_total > 0"
                                class="border-t border-default bg-elevated/40">
                                <td colspan="9" class="px-3 py-2 text-sm text-muted flex flex-wrap gap-x-6 gap-y-1">
                                    <span v-if="item.description"><strong class="text-highlighted">Description:</strong>
                                        {{ item.description }}</span>
                                    <span v-if="item.extra_service_name">
                                        <strong class="text-highlighted">Extra:</strong> {{ item.extra_service_name }}
                                        ({{ formatCurrency(item.extra_service_price) }})
                                    </span>
                                    <span v-if="item.discount > 0">
                                        <strong class="text-highlighted">Discount:</strong> −{{
                                            formatCurrency(item.discount) }}
                                    </span>
                                    <span v-if="item.notes"><strong class="text-highlighted">Notes:</strong> {{
                                        item.notes }}</span>
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Payments -->
        <section>
            <h2 class="text-lg font-semibold text-highlighted mb-3">Payments ({{ jobOrder.payments.length }})</h2>
            <div v-if="jobOrder.payments.length" class="border border-default rounded-md overflow-hidden">
                <table class="w-full text-base">
                    <thead class="bg-elevated">
                        <tr class="text-left text-sm text-muted uppercase">
                            <th class="p-3">Date</th>
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
                            <td class="p-3 text-highlighted">{{ payment.account_name }}</td>
                            <td class="p-3 font-semibold text-highlighted">{{ formatCurrency(payment.amount) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-else class="text-muted text-base border border-default rounded-md p-4 text-center">No payments recorded
                yet.
            </p>
        </section>

        <!-- Claiming History -->
        <section>
            <h2 class="text-lg font-semibold text-highlighted mb-3">Claiming History ({{ jobOrder.claims.length }})</h2>
            <p v-if="!jobOrder.claims.length"
                class="text-muted text-base border border-default rounded-md p-4 text-center">
                No items have been claimed yet.
            </p>
            <!-- populate a table here the same way as Payments once claims have data -->
        </section>
    </div>
</template>