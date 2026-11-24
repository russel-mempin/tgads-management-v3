<script setup lang="ts">
// Dependecy imports
import { computed, resolveComponent, h, ref } from 'vue';
import type { TableColumn, RadioGroupItem } from '@nuxt/ui';
// Type imports
import type { MonthlyPerformance, CustomerPerformance, JobOrderSales, ServicePerformance } from '@/types/performance';
// Component imports
import { formatCurrency, formatDate } from '@/utils/formatters';
import { useReferenceStore } from '@/stores/reference';
import ExpenseTable from './ExpenseTable.vue';
import TransactionsTable from './TransactionsTable.vue';

const referenceStore = useReferenceStore()

const props = defineProps<{
    data: MonthlyPerformance
}>()

const totalEndingBalance = computed(() =>
    props.data.snapshots_of_accounts.reduce(
        (total, account) => total + Number(account.ending_balance),
        0
    )
)

// Accounts Choices
const items = computed<RadioGroupItem[]>(() => [
    {
        label: 'All',
        value: 'all',
        class: 'w-30'
    },
    ...referenceStore.accountOptions.map(account => ({
        label: account.name,
        value: account.name,
        class: 'w-30'
    }))
])

const salesItems = ref<RadioGroupItem[]>([
    {
        label: 'All',
        value: 'System',
        class: 'w-36'
    },
    {
        label: 'Receivables',
        value: 'Light',
        class: 'w-36'
    },
    {
        label: 'No Balance',
        value: 'Dark',
        class: 'w-36'
    }
])

// Filtering variables
const selectedCollectionsAccount = ref<string>('all')
const selectedExpensesAccount = ref<string>('all')

const filteredCollectedList = computed(() => {
    if (selectedCollectionsAccount.value === 'all') {
        return props.data.collected_list
    }

    return props.data.collected_list.filter(
        transaction => transaction.account_name === selectedCollectionsAccount.value
    )
})
const filteredExpenseList = computed(() => {
    if (selectedExpensesAccount.value === 'all') {
        return props.data.expenses_list
    }

    return props.data.expenses_list.filter(
        expense => expense.account_name === selectedExpensesAccount.value
    )
})
const totalCollected = computed(() =>
    filteredCollectedList.value.reduce(
        (total, transaction) => total + Number(transaction.amount),
        0
    )
)
const totalExpense = computed(() =>
    filteredExpenseList.value.reduce(
        (total, expense) => total + Number(expense.amount),
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

const serviceColumns: TableColumn<ServicePerformance>[] = [
    {
        accessorKey: 'full_service_name',
        header: 'Name',
    },
    {
        accessorKey: 'order_quantity',
        header: 'Order Quantity',
    },
    {
        accessorKey: 'material_consumed_in_sqft',
        header: 'Material Consumed (sqft.)',
    },
    {
        accessorKey: 'sales',
        header: 'Sales',
        cell: ({ row }) => `${formatCurrency(row.getValue('sales'))}`
    },
    {
        accessorKey: 'sales_percentage',
        header: 'sales_percentage',
        cell: ({ row }) => `${row.original.sales_percentage.toFixed(1)}%`,
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
        <!-- Account Snapshots -->
        <div class="flex gap-6 justify-between">
            <div v-for="account in data.snapshots_of_accounts" class="flex-1 border border-default rounded-md">
                <p class="border-b border-default p-4 bg-elevated rounded-t-md">{{ account.account_name }}</p>
                <div class="px-4 py-2 flex items-center justify-between border-b border-default">
                    <p class="text-xs font-semibold uppercase text-muted">Collections</p>
                    <p class="text-lg font-semibold" :class="{
                        'text-green-600': Number(account.collections) !== 0,
                        'text-default': Number(account.collections) === 0
                    }">
                        {{ formatCurrency(Number(account.collections)) }}
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
        <div class="mt-6 border border-default rounded-md">
            <div class="p-4 flex items-center justify-between border-b border-default">
                <p class="font-semibold uppercase text-muted">Collections List</p>
                <URadioGroup v-model="selectedCollectionsAccount" size="sm" indicator="hidden" orientation="horizontal"
                    variant="table" default-value="Cash" :items="items" />
            </div>
            <div class="max-h-100 overflow-y-auto">
                <TransactionsTable :data="filteredCollectedList" />
            </div>
            <p class="border-t border-default p-4 text-end font-semibold uppercase bg-elevated rounded-b-md">Total: {{
                formatCurrency(totalCollected) }}</p>
        </div>
        <!-- Expenses Section -->
        <div class="flex gap-6">
            <div class="flex-1 mt-6 border border-default rounded-md">
                <div class="p-4 flex items-center justify-between border-b border-default">
                    <p class="font-semibold uppercase text-muted">Expense List</p>
                    <URadioGroup v-model="selectedExpensesAccount" size="sm" indicator="hidden" orientation="horizontal"
                        variant="table" default-value="Cash" :items="items" />
                </div>
                <div class="max-h-100 overflow-y-auto">
                    <ExpenseTable :expense="filteredExpenseList" />
                </div>
                <p class="border-t border-default p-4 text-end font-semibold uppercase bg-elevated rounded-b-md">Total:
                    {{ formatCurrency(totalExpense) }}</p>
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
            <div class="p-4 flex items-center justify-between border-b border-default">
                <p class="font-semibold uppercase text-muted">Job Order Sales List</p>
                <URadioGroup size="xs" indicator="hidden" orientation="horizontal" variant="table" default-value="All"
                    :items="salesItems" />
            </div>
            <div class="max-h-100 overflow-y-auto">
                <UTable :data="data.job_order_sales" :columns="salesColumns" />
            </div>
        </div>
        <!-- Service Performance -->
        <div class="mt-6 border border-default rounded-md">
            <p class="p-4 border-b border-default font-semibold uppercase text-muted">Top Services</p>
            <UTable :data="data.service_performances" :columns="serviceColumns" />
        </div>
        <!-- Customers Section -->
        <div class="mt-6 border border-default rounded-md">
            <p class="p-4 border-b border-default font-semibold uppercase text-muted">Top
                Customers</p>
            <UTable :data="data.customer_performances" :columns="customerColumns" />
        </div>
    </div>
</template>