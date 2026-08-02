<script setup lang="ts">
import { ref, h, resolveComponent } from 'vue'
import type { Payment } from '@/types/jobOrder';
import type { TableColumn } from '@nuxt/ui';
import { formatDate, formatCurrency } from '@/utils/formatters';
import PaymentForm from './PaymentForm.vue';

const props = defineProps<{
    payments: Payment[]
}>()

const emit = defineEmits<{
    addPayment: [payment: Payment]
    removePayment: [referenceNumber: string]
    updatePayment: [index: number, payment: Payment]
}>()

// UI Variables
const isOpen = ref(false)
const UButton = resolveComponent('UButton')
const isDeleteConfirmOpen = ref(false)
const itemPendingDelete = ref<Payment | null>(null)

// Data Variables
const itemPendingEdit = ref<Payment | null>(null)
const itemPendingEditIndex = ref<number | null>(null)

// UI Functions
const openAddForm = () => {
    itemPendingEdit.value = null
    itemPendingEditIndex.value = null
    isOpen.value = true
}

const requestRemovePayment = (item: Payment) => {
    itemPendingDelete.value = item
    isDeleteConfirmOpen.value = true
}

const confirmRemovePayment = () => {
    if (!itemPendingDelete.value) return
    emit('removePayment', itemPendingDelete.value.reference_number)
    isDeleteConfirmOpen.value = false
    itemPendingDelete.value = null
}

const cancelRemovePayment = () => {
    isDeleteConfirmOpen.value = false
    itemPendingDelete.value = null
}

const requestEditPayment = (payment: Payment, index: number) => {
    itemPendingEdit.value = payment
    itemPendingEditIndex.value = index
    isOpen.value = true
}

// Data functions
const handleSave = (payment: Payment) => {
    if (itemPendingEditIndex.value !== null) {
        emit('updatePayment', itemPendingEditIndex.value, payment)
    } else {
        emit('addPayment', payment)
    }
    itemPendingEdit.value = null
    itemPendingEditIndex.value = null
}

// Table Display
const columns: TableColumn<Payment>[] = [
    {
        accessorKey: 'date_received',
        header: 'Date Received',
        cell: ({ row }) => `${formatDate(row.original.date_received)}`
    },
    { accessorKey: 'reference_number', header: 'Reference No.' },
    {
        accessorKey: 'amount',
        header: 'Amount',
        cell: ({ row }) => `${formatCurrency(row.original.amount)}`
    },
    { accessorKey: 'account_name_snapshot', header: 'Method' },
    { accessorKey: 'notes', header: 'Notes', cell: ({ row }) => row.original.notes || '—', },
    {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) =>
            h('div', { class: 'flex items-center gap-2' }, [
                h(UButton, {
                    color: 'warning',
                    variant: 'ghost',
                    icon: 'i-lucide-square-pen',
                    size: 'md',
                    onClick: (e: Event) => {
                        e.stopPropagation()
                        requestEditPayment(row.original, row.index)
                    }
                }),
                h(UButton, {
                    icon: 'i-lucide-trash-2',
                    color: 'error',
                    variant: 'ghost',
                    size: 'md',
                    onClick: (e: Event) => {
                        e.stopPropagation()
                        requestRemovePayment(row.original)
                    },
                }),
            ])
    }
]
</script>

<template>
    <UModal v-model:open="isDeleteConfirmOpen" title="Delete Payment?">
        <template #body>
            <p class="text-sm text-muted">
                Are you sure you want to delete payment info for reference number
                <span class="font-semibold text-highlighted">{{ itemPendingDelete?.reference_number }}</span>
                amounting to {{ formatCurrency(itemPendingDelete?.amount) }}? This can't be undone.
            </p>
            <div class="flex justify-end gap-3 mt-6">
                <UButton label="Cancel" color="neutral" variant="outline" @click="cancelRemovePayment" />
                <UButton label="Delete" color="error" @click="confirmRemovePayment" />
            </div>
        </template>
    </UModal>
    <PaymentForm v-model:isOpen="isOpen" :editing-payment="itemPendingEdit" @save="handleSave" />
    <div class="bg-default border border-default rounded-md p-6 m-8">
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-2">
                <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <p class="font-semibold text-highlighted">Payments</p>
            </div>
            <UButton @click="openAddForm" label="Add Payment" icon="i-lucide-plus" />
        </div>
        <!-- Empty state -->
        <div v-if="!payments.length" class="text-sm text-muted text-center">
            No payments recorded yet.
        </div>
        <UTable v-else :data="payments" :columns="columns" class="border border-default rounded-md" />
    </div>
</template>