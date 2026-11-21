<script setup lang="ts">
import { computed, resolveComponent, h } from 'vue';
import type { MonthlyPerformance, CustomerPerformance, JobOrderSales } from '@/types/performance';
import type { Expense } from '@/types/expense';
import { formatCurrency, formatDate, mapExpenseCategory } from '@/utils/formatters';
import type { TableColumn } from '@nuxt/ui';

const UBadge = resolveComponent('UBadge')

const props = defineProps<{
    data: MonthlyPerformance
}>()

const totalEndingBalance = computed(() =>
    props.data.snapshots_of_accounts.reduce(
        (total, account) => total + Number(account.ending_balance),
        0
    )
)

const customerColumns: TableColumn<CustomerPerformance>[] = [
    {
        id: 'rank',
        cell: ({ row }) => row.index + 1,
    },
    {
        accessorKey: 'name',
        header: 'Name',
    },
    {
        accessorKey: 'order_quantity',
        header: 'Orders',
    },
    {
        accessorKey: 'sales',
        header: 'Sales',
        cell: ({ row }) => formatCurrency(Number(row.original.sales)),
    },
    {
        accessorKey: 'balance',
        header: 'Balance',
        cell: ({ row }) => formatCurrency(Number(row.original.balance)),
    },
    {
        accessorKey: 'sales_percentage',
        header: 'Sales %',
        cell: ({ row }) => `${row.original.sales_percentage.toFixed(1)}%`,
    },
    {
        accessorKey: 'last_order',
        header: 'Last Order',
        cell: ({ row }) => `${formatDate(row.original.last_order)}`,
    },
]

const expenseColumns: TableColumn<Expense>[] = [
    {
        accessorKey: 'date',
        header: 'Date',
        cell: ({ row }) => `${formatDate(row.getValue('date'))}`
    },
    {
        accessorKey: 'category',
        header: 'Category',
        cell: ({ row }) => {
            const category = row.getValue('category') as string
            return h(UBadge, { class: mapExpenseCategory(category) },
                () => category
            )
        }
    },
    {
        accessorKey: 'description',
        header: 'Description',
    },
    {
        accessorKey: 'amount',
        header: 'Amount',
        cell: ({ row }) => `${formatCurrency(row.getValue('amount'))}`
    },
    {
        accessorKey: 'account_name',
        header: 'Method',
    },
    {
        accessorKey: 'created_by_name',
        header: 'Created By',
    },
]

const salesColumns: TableColumn<JobOrderSales>[] = [
    {
        accessorKey: 'jo_number',
        header: 'JO Number',
    },
    {
        accessorKey: 'customer_name',
        header: 'Customer Name',
        cell: ({ row }) => row.getValue('customer_name') || 'Walk-in',
    },
    {
        accessorKey: 'date_received',
        header: 'Date Received',
        cell: ({ row }) => `${formatDate(row.getValue('date_received'))}`
    },
    {
        accessorKey: 'total_due',
        header: 'Total Due',
        cell: ({ row }) => `${formatCurrency(row.getValue('total_due'))}`
    },
    {
        accessorKey: 'total_paid',
        header: 'Total Paid',
        cell: ({ row }) => `${formatCurrency(row.getValue('total_paid'))}`
    },
    {
        accessorKey: 'balance',
        header: 'Balance',
        cell: ({ row }) => {
            const balance = Number(row.getValue('balance'))
            return h(
                'span',
                {
                    class: balance === 0 ? 'text-green-600' : 'text-red-600'
                },
                formatCurrency(balance)
            )
        }
    },
]
</script>

<template>
    <div class="p-2">
        <h3 class="text-sm font-semibold uppercase text-muted">Monthly Performance Details</h3>
        <div class="py-4 flex items-center justify-between">
            <p class="font-semibold uppercase text-muted">Accounts</p>
            <p class="font-semibold uppercase text-muted">Total: {{ formatCurrency(totalEndingBalance) }}</p>
        </div>
        <div class="flex gap-6 justify-between">
            <div v-for="account in data.snapshots_of_accounts" class="flex-1 border border-default rounded-md">
                <p class="border-b border-default p-4 bg-elevated rounded-t-md">{{ account.account_name }}</p>
                <div class="px-4 py-2 flex items-center justify-between border-b border-default">
                    <p class="text-xs font-semibold uppercase text-muted">Collections</p>
                    <p class="text-lg font-semibold" :class="{
                        'text-green-600': Number(account.deductions) !== 0,
                        'text-default': Number(account.deductions) === 0
                    }">
                        {{ formatCurrency(Number(account.deductions)) }}
                    </p>
                </div>
                <div class="px-4 py-2 flex items-center justify-between border-b border-default">
                    <p class="text-xs font-semibold uppercase text-muted">Deductions</p>
                    <p class="text-lg font-semibold" :class="{
                        'text-red-600': Number(account.deductions) !== 0,
                        'text-default': Number(account.deductions) === 0
                    }">
                        {{ formatCurrency(Number(account.deductions)) }}
                    </p>
                </div>
                <div class="px-4 py-2 flex items-center justify-between bg-accented rounded-b-md">
                    <p class="text-xs font-semibold uppercase text-muted">Ending Balance</p>
                    <p class="text-lg font-semibold" :class="Number(account.ending_balance) < 0 ? 'text-red-600' : ''">
                        {{ formatCurrency(Number(account.ending_balance)) }}
                    </p>
                </div>
            </div>
        </div>
        <!-- Collected Section -->

        <!-- Expenses Section -->
        <div class="flex gap-6">
            <div class="flex-1 mt-6 border border-default rounded-md">
                <div class="p-4 flex items-center justify-between border-b border-default">
                    <p class="font-semibold uppercase text-muted">Expense List</p>
                    <p class="font-semibold uppercase text-error">Total: {{ formatCurrency(Number(data.expenses)) }}</p>
                </div>
                <div class="max-h-100 overflow-y-auto">
                    <UTable :data="data.expenses_list" :columns="expenseColumns" />
                </div>
            </div>
            <div class="mt-6 border border-default rounded-md">
                <p class="p-4 font-semibold uppercase text-muted border-b border-default">Expenses By Category (Pie
                    Chart)</p>
                <div>
                    <VueApexCharts type="pie" height="350" />
                </div>
            </div>
        </div>
        <!-- Sales List (TODO: Toggle to see all or with balances only to see collectibles)-->
        <div class="mt-6 border border-default rounded-md">
            <div>
                <p class="p-4 border-b border-default font-semibold uppercase text-muted">Job Order Sales List</p>
            </div>
            <div class="max-h-100 overflow-y-auto">
                <UTable :data="data.job_order_sales" :columns="salesColumns" />
            </div>
        </div>
        <!-- Customers Section -->
        <div class="mt-6 border border-default rounded-md">
            <p class="p-4 border-b border-default font-semibold uppercase text-muted">Top
                Customers</p>
            <UTable :data="data.customer_performances" :columns="customerColumns" />
        </div>
    </div>
</template>