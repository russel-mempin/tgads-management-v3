<script setup lang="ts">
import { onMounted, ref, h, resolveComponent } from 'vue'
import { getForReview } from '@/api/job_orders';
import type { JobOrder } from '@/types/job_ordersTypes';
import type { TableColumn } from '@nuxt/ui';
import { useRouter } from 'vue-router';
import { formatCurrency, formatDate } from '@/utils/formatters';

const router = useRouter()
const job_orders = ref<JobOrder[]>([])
const loading = ref(false)
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')

const fetchServices = async () => {
    job_orders.value = await getForReview()
    console.log(job_orders.value)
}

onMounted(async () => {
    fetchServices()
})

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
                        router.push(`/job-orders/view/${row.original.jo_number}`)
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
                        router.push(`/job-orders/print/${row.original.jo_number}`)
                    }
                })
            ])
    }
]
</script>

<template>
    <section class="border border-default rounded-md">
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
                                        <td class="p-2.5 text-highlighted">{{ item.height && item.width ?
                                            `${item.height} × ${item.width} ${item.size_unit}` : '—' }}</td>
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