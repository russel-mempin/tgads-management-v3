<script setup lang="ts">
// Dependency imports
import { ref, onMounted } from 'vue';
// Type imports
import type { Transfer, TransferCreate, TransferUpdate } from '@/types/transfer';
// Component imports
import { useAuthStore } from '@/stores/auth';
import { archiveTransfer, getAllTransfers, createTransfer, updateTransfer } from '@/api/transfer';
import TransfersTable from '@/components/TransfersTable.vue';
import TransferForm from '@/components/TransferForm.vue';
import { formatDate } from '@/utils/formatters';
import ConfirmModalWithDetails from '@/components/ConfirmModalWithDetails.vue';

const authStore = useAuthStore()
const toast = useToast()

// UI Variables
const loading = ref(false)
const isAddTransferFormOpen = ref(false)
const isConfirmVoidModalOpen = ref(false)

// Data Variables
const selectedTransfer = ref<Transfer>()
const originalTransfer = ref<Transfer>()
const data = ref<Transfer[]>([])

// Filtering
const descriptionSearch = ref('')
const includeArchived = ref(false)

// UI Functions
const openAddTransferForm = () => {
    selectedTransfer.value = undefined
    originalTransfer.value = undefined
    isAddTransferFormOpen.value = true
}
const openEditTransferForm = (transfer: Transfer) => {
    selectedTransfer.value = transfer
    originalTransfer.value = { ...transfer }
    isAddTransferFormOpen.value = true
}
const openVoidTransferModal = (transfer: Transfer) => {
    selectedTransfer.value = transfer
    isConfirmVoidModalOpen.value = true
}

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllTransfers(
            includeArchived.value,
            descriptionSearch.value,
        )
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    await fetchData()
})

const saveNewTransferToDb = async (item: TransferCreate) => {
    try {
        if (!selectedTransfer.value) {
            await createTransfer(item)
            toast.add({
                title: 'Transfer Added.',
                color: 'success',
                icon: 'i-lucide-circle-check'
            })
        }
        else {
            const changes: TransferUpdate = {}
            const keys = ['reference_number', 'transferred_at', 'description', 'amount', 'source_account_id', 'destination_account_id'] as const

            for (const key of keys) {
                const currentValue = item[key]
                const originalValue = originalTransfer.value?.[key]

                const changed =
                    key === 'transferred_at'
                        ? new Date(currentValue as string).getTime() !==
                        new Date(originalValue as string).getTime()
                        : key === 'amount'
                            ? Number(currentValue) !== Number(originalValue)
                            : currentValue !== originalValue
                if (changed) {
                    changes[key] = currentValue as never
                }
            }
            await updateTransfer(selectedTransfer.value.id, changes)
            toast.add({
                title: 'Transfer Updated.',
                color: 'success',
                icon: 'i-lucide-circle-check'
            })
        }
        await fetchData()
        selectedTransfer.value = undefined
        originalTransfer.value = undefined
    }
    catch (error: unknown) {
        console.error('Error saving transfer:', error)
        toast.add({
            title: 'Error saving transfer.',
            color: 'error',
            icon: 'i-lucide-alert-circle'
        })
    }
    finally {
        isAddTransferFormOpen.value = false
    }
}

const confirmArchiveTransfer = async () => {
    if (!selectedTransfer.value) return
    try {
        await archiveTransfer(selectedTransfer.value.id)
        toast.add({
            title: 'Transfer Archived.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchData()
    }
    catch (error: unknown) {
        console.error('Error archiving transfer:', error)
        toast.add({
            title: 'Error archiving transfer.',
            color: 'error',
            icon: 'i-lucide-alert-circle'
        })
    }
    finally {
        isConfirmVoidModalOpen.value = false
        selectedTransfer.value = undefined
    }
}
</script>

<template>
    <ConfirmModalWithDetails v-model:open="isConfirmVoidModalOpen" @confirm="confirmArchiveTransfer" title="You are about to void a transfer"
        description="This will archive the transfer data and reverse the transaction related to it.">
        <template #details>
            <div class="flex justify-between gap-4">
                <span class="text-sm text-muted">Description</span>
                <span class="text-sm font-medium text-highlighted">
                    {{ selectedTransfer?.description }}
                </span>
            </div>

            <div class="mt-2 flex justify-between gap-4">
                <span class="text-sm text-muted">Amount</span>
                <span class="text-sm font-medium text-highlighted">
                    ₱{{ selectedTransfer?.amount }}
                </span>
            </div>

            <div class="mt-2 flex justify-between gap-4">
                <span class="text-sm text-muted">Transfer Date</span>
                <span class="text-sm font-medium text-highlighted">
                    {{ formatDate(selectedTransfer?.transferred_at) }}
                </span>
            </div>
        </template>
    </ConfirmModalWithDetails>
    <TransferForm v-model:is-open="isAddTransferFormOpen" @save="saveNewTransferToDb"
        :editing-transfer="selectedTransfer" />
    <div class="h-full min-h-0 flex flex-col">
        <section class="shrink-0 mt-6 px-6 flex gap-6 items-center">
            <UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
            <USwitch v-if="authStore.isOwner" label="Include archived" v-model="includeArchived" />
            <UButton label="Add Transfer" icon="i-lucide-plus" color="primary" size="lg" @click="openAddTransferForm" />
        </section>
        <section class="bg-default flex-1 min-h-0 m-6 border border-default rounded-md overflow-hidden">
            <TransfersTable :transfer="data">
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditTransferForm(item)" />
                    <UButton icon="i-lucide-eye-off" variant="ghost" color="error" size="md"
                        @click="openVoidTransferModal(item)" />
                </template>
            </TransfersTable>
        </section>
        <!-- <section class="shrink-0 mb-6 px-6 flex items-center justify-between">
            <p class="text-muted text-sm">
                Showing
                {{ data.length ? currentOffset + 1 : 0 }}–{{
                    Math.min(currentOffset + data.length, totalRecords)
                }}
                of {{ totalRecords }}
            </p>

            <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
        </section> -->
    </div>
</template>