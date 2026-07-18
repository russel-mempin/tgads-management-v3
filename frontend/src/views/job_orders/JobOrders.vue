<script setup lang="ts">
import { ref, onMounted, resolveComponent, h, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getJobOrderKpis, getAllJobOrders, getJobOrderCount } from '@/api/job_orders'
import type { JobOrder } from '@/types/job_ordersTypes'
import type { TableColumn } from '@nuxt/ui'
import { formatDate, formatCurrency } from '@/utils/formatters'
import { useRouter } from 'vue-router'
import { refDebounced } from '@vueuse/core'

const authStore = useAuthStore()
const job_orders = ref<JobOrder[]>([])
const kpis = ref<Record<string, any>>({})
const activeFilter = ref<string | null>(null)
const joNumberSearch = ref('');
const jobStatus = ref('');
const paymentStatus = ref('');
const currentOffset = ref(0)
const paymentStatusOptions = ref(['Fully Paid', 'Partial', 'Unpaid', 'Credit', 'Refunded', 'Overcharged']);
const jobStatusOptions = ref(['Pending', 'For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled']);
const loading = ref(false)
const rows = ref(10)
const totalRecords = ref(0)
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const router = useRouter()
const debouncedSearch = refDebounced(joNumberSearch, 400)

const fetchServices = async () => {
    loading.value = true
    const filterParams = {
        offset: currentOffset.value,
        limit: rows.value,
        payment_status: paymentStatus.value || undefined,
        job_status: jobStatus.value || undefined,
        search: debouncedSearch.value || undefined,
        filter: activeFilter.value || undefined,
    }
    const [data, count] = await Promise.all([
        getAllJobOrders(filterParams),
        getJobOrderCount(filterParams)
    ])
    job_orders.value = data
    totalRecords.value = count
    loading.value = false
}

onMounted(async () => {
    fetchServices()
    kpis.value = await getJobOrderKpis()
})

const currentPage = computed({
    get: () => Math.floor(currentOffset.value / rows.value) + 1,
    set: (page: number) => {
        currentOffset.value = (page - 1) * rows.value
        fetchServices()
    }
})


const clearFilters = () => {
    joNumberSearch.value = ''
    jobStatus.value = ''
    paymentStatus.value = ''
    currentOffset.value = 0
    fetchServices()
}

const setFilter = (filter: string) => {
    activeFilter.value = activeFilter.value === filter ? null : filter
    clearFilters()
}

const viewJobOrder = (jo_number: number) => {
    router.push(`/job-orders/view/${jo_number}`)
}

const printJobOrder = (jo_number: number) => {
    router.push(`/job-orders/print/${jo_number}`)
}

const columns: TableColumn<JobOrder>[] = [
    {
        id: 'expand',
        cell: ({ row }) =>
            h(UButton, {
                color: 'neutral',
                variant: 'ghost',
                icon: 'i-lucide-chevron-down',
                square: true,
                'aria-label': 'Expand',
                ui: {
                    leadingIcon: [
                        'transition-transform',
                        row.getIsExpanded() ? 'duration-200 rotate-180' : ''
                    ]
                },
            })
    },
    {
        accessorKey: 'jo_number',
        header: '#',
        cell: ({ row }) => `#${row.getValue('jo_number')}`
    },
    {
        accessorKey: 'customer_name',
        header: 'Customer',
        cell: ({ row }) => `${row.getValue('customer_name')}`
    },
    {
        accessorKey: 'date_received',
        header: 'Start Date',
        cell: ({ row }) => `${formatDate(row.getValue('date_received'))}`
    },
    {
        accessorKey: 'payment_status',
        header: 'Payment',
        cell: ({ row }) => {
            const color = {
                'Fully Paid': 'success' as const,
                'Partial': 'warning' as const,
                'Unpaid': 'error' as const,
                'Credit': 'info' as const,
                'Refunded': 'neutral' as const,
                'Overcharged': 'warning' as const,
            }[row.getValue('payment_status') as string]

            return h(UBadge, { class: 'capitalize font-semibold', variant: 'soft', color }, () =>
                row.getValue('payment_status')
            )
        }
    },
    {
        accessorKey: 'overall_job_status',
        header: 'Job Status',
        cell: ({ row }) => {
            const color = {
                'Pending': 'warning' as const,
                'For Layout': 'info' as const,
                'For Approval': 'primary' as const,
                'For Printing': 'primary' as const,
                'For Pickup': 'success' as const,
                'Released': 'neutral' as const,
                'Cancelled': 'error' as const,
            }[row.getValue('overall_job_status') as string]

            return h(UBadge, { class: 'capitalize font-semibold', variant: 'soft', color }, () =>
                row.getValue('overall_job_status')
            )
        }
    },
    {
        accessorKey: 'total_due',
        header: 'Balance',
        cell: ({ row }) => formatCurrency(row.original.total_due - row.original.total_paid)
    },
    {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) =>
            h('div', { class: 'flex items-center gap-2' }, [
                h(UButton, {
                    color: 'neutral',
                    variant: 'outline',
                    icon: 'i-lucide-eye',
                    label: 'View',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        viewJobOrder(row.original.jo_number)
                    }
                }),
                h(UButton, {
                    color: 'neutral',
                    variant: 'outline',
                    icon: 'i-lucide-printer',
                    label: 'Print',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        printJobOrder(row.original.jo_number)
                    }
                })
            ])
    }
]

watch([debouncedSearch, jobStatus, paymentStatus], () => {
    currentOffset.value = 0
    fetchServices()
})
</script>

<template>
    <!-- Operation KPI's -->
    <section v-if="authStore.isLoggedIn" class="grid grid-cols-4 gap-4">
        <div @click="setFilter('overdue')"
            class="border shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'overdue'
                ? 'bg-orange-100 dark:bg-orange-950/40 border-orange-200 dark:border-orange-900'
                : 'bg-default border-default hover:bg-orange-50 dark:hover:bg-orange-950/20'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-orange-700 dark:text-orange-400"
                :class="activeFilter === 'overdue' ? 'bg-orange-300 dark:bg-orange-900' : 'bg-orange-100 dark:bg-orange-950/60'">
                <UIcon name="i-lucide-file-warning" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-muted">Overdue Jobs</p>
                <p class="font-bold text-3xl text-orange-700 dark:text-orange-400">{{ kpis.overdue_jobs }}</p>
            </div>
        </div>
        <div @click="setFilter('in-progress')"
            class="border shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'in-progress'
                ? 'bg-blue-100 dark:bg-blue-950/40 border-blue-200 dark:border-blue-900'
                : 'bg-default border-default hover:bg-blue-50 dark:hover:bg-blue-950/20'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-blue-700 dark:text-blue-400"
                :class="activeFilter === 'in-progress' ? 'bg-blue-300 dark:bg-blue-900' : 'bg-blue-100 dark:bg-blue-950/60'">
                <UIcon name="i-lucide-clock" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-muted">In Progress</p>
                <p class="font-bold text-3xl text-blue-700 dark:text-blue-400">{{ kpis.in_progress }}</p>
            </div>
        </div>
        <div @click="setFilter('due-today')"
            class="border shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'due-today'
                ? 'bg-yellow-100 dark:bg-yellow-950/40 border-yellow-200 dark:border-yellow-900'
                : 'bg-default border-default hover:bg-yellow-50 dark:hover:bg-yellow-950/20'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-red-700 dark:text-red-400"
                :class="activeFilter === 'due-today' ? 'bg-yellow-300 dark:bg-yellow-900' : 'bg-yellow-100 dark:bg-yellow-950/60'">
                <UIcon name="i-lucide-clock-fading" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-muted">Due Today</p>
                <p class="font-bold text-3xl text-red-700 dark:text-red-400">{{ kpis.due_today }}</p>
            </div>
        </div>
        <div @click="setFilter('for-pickup')"
            class="border shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'for-pickup'
                ? 'bg-green-100 dark:bg-green-950/40 border-green-200 dark:border-green-900'
                : 'bg-default border-default hover:bg-green-50 dark:hover:bg-green-950/20'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-green-700 dark:text-green-400"
                :class="activeFilter === 'for-pickup' ? 'bg-green-300 dark:bg-green-900' : 'bg-green-100 dark:bg-green-950/60'">
                <UIcon name="i-lucide-printer-check" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-muted">Ready for pickup</p>
                <p class="font-bold text-3xl text-green-700 dark:text-green-400">{{ kpis.ready_for_pickup }}</p>
            </div>
        </div>
    </section>
    <!-- Controls -->
    <section class="mt-4 flex gap-4">
        <UInput size="lg" class="flex-1" v-model="joNumberSearch"
            placeholder="Search by customer name or JO Number..." />
        <USelect size="lg" class="w-50" v-model="paymentStatus" :items="paymentStatusOptions"
            placeholder="Payment Status" showClear />
        <USelect size="lg" class="w-50" v-model="jobStatus" :items="jobStatusOptions" placeholder="Job Status"
            showClear />
        <UButton size="lg" icon="i-lucide-funnel-x" label="Clear Filters" color="neutral" variant="soft"
            @click="clearFilters" />
        <UButton size="lg" icon="i-lucide-file-plus-corner" label="Add Job Order" color="primary" variant="solid"
            @click="clearFilters" />
    </section>
    <section class="mt-4 border border-default rounded-md">
        <UTable :data="job_orders" :columns="columns" :loading="loading" @select="(e, row) => row.toggleExpanded()" :ui="{
            th: 'text-muted font-semibold uppercase',
            td: 'text-base text-highlighted',
            tr: 'hover:bg-elevated/100 odd:bg-elevated/50 cursor-pointer'
        }">
            <template #expanded="{ row }">
                <div class="p-2 flex flex-col gap-4">
                    <!-- Job Items -->
                    <div>
                        <p class="text-sm font-semibold text-muted uppercase mb-2">
                            Job Items ({{ row.original.job_items.length }})
                        </p>
                        <div v-if="row.original.job_items.length"
                            class="border border-default rounded-md overflow-hidden bg-default">
                            <table class="w-full text-sm">
                                <thead class="bg-elevated">
                                    <tr class="text-left text-muted uppercase">
                                        <th class="p-2.5">Item</th>
                                        <th class="p-2.5">Service</th>
                                        <th class="p-2.5">Size</th>
                                        <th class="p-2.5">Unit Price</th>
                                        <th class="p-2.5">Qty</th>
                                        <th class="p-2.5">Subtotal</th>
                                        <th class="p-2.5">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in row.original.job_items" :key="item.item_id"
                                        class="border-t border-default">
                                        <td class="p-2.5 text-highlighted">{{ item.item_id }}</td>
                                        <td class="p-2.5 text-highlighted">
                                            {{ item.service_name_snapshot }}
                                            <span v-if="item.service_option_name_snapshot" class="text-muted"> — {{
                                                item.service_option_name_snapshot }}</span>
                                        </td>
                                        <td class="p-2.5 text-highlighted">{{ item.height && item.width ? `${item.height} × ${item.width} ${item.size_unit}` : '—' }}</td>
                                        <td class="p-2.5 text-highlighted">{{ formatCurrency(item.unit_price) }}</td>
                                        <td class="p-2.5 text-highlighted">{{ item.quantity }}</td>
                                        <td class="p-2.5 font-semibold text-highlighted">{{
                                            formatCurrency(item.subtotal) }}</td>
                                        <td class="p-2.5">
                                            <UBadge variant="soft" color="neutral" class="font-semibold">{{
                                                item.job_status }}</UBadge>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <p v-else class="text-muted text-sm">No job items recorded.</p>
                    </div>

                    <!-- Payments -->
                    <div>
                        <p class="text-sm font-semibold text-muted uppercase mb-2">
                            Payments ({{ row.original.payments.length }})
                        </p>
                        <div v-if="row.original.payments.length"
                            class="border border-default rounded-md overflow-hidden bg-default">
                            <table class="w-full text-sm">
                                <thead class="bg-elevated">
                                    <tr class="text-left text-muted uppercase">
                                        <th class="p-2.5">Date</th>
                                        <th class="p-2.5">Reference #</th>
                                        <th class="p-2.5">Method</th>
                                        <th class="p-2.5">Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="payment in row.original.payments" :key="payment.reference_number"
                                        class="border-t border-default">
                                        <td class="p-2.5 text-highlighted">{{ formatDate(payment.date_received) }}</td>
                                        <td class="p-2.5 text-highlighted">{{ payment.reference_number }}</td>
                                        <td class="p-2.5 text-highlighted">{{ payment.account_name }}</td>
                                        <td class="p-2.5 font-semibold text-highlighted">{{
                                            formatCurrency(payment.amount) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <p v-else class="text-muted text-sm">No payments recorded yet.</p>
                    </div>
                </div>
            </template>
        </UTable>
    </section>
    <section class="mt-4 flex items-center justify-between">
        <p class="text-muted text-sm">
            Showing {{ job_orders.length ? currentOffset + 1 : 0 }}–{{ Math.min(currentOffset + rows, totalRecords) }}
            of {{ totalRecords }}
        </p>
        <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
    </section>
</template>