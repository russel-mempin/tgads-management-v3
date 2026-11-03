<script setup lang="ts">
import type { Transfer } from '@/types/transfer';
import type { TableColumn } from '@nuxt/ui';
import { formatDate, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
    transfer: Transfer[]
}>()

const columns: TableColumn<Transfer>[] = [
    {
        accessorKey: 'reference_number',
        header: 'Reference No.',
        cell: ({ row }) => row.getValue('reference_number') || '—',
    },
    {
        accessorKey: 'transferred_at',
        header: 'Transferred At',
        cell: ({ row }) => `${formatDate(row.getValue('transferred_at'))}`
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
        id: 'movement',
        header: 'Movement',
    },
    {
        accessorKey: 'updated_by_name',
        header: 'Last Updated By',
    },
    {
        id: 'actions',
        header: ''
    }
]
// TODO: When updated by is hovered, show creator and timestamps.
</script>

<template>
    <UTable :data="transfer" :columns="columns" sticky class="overflow-y-auto h-full">
        <template #movement-cell="{ row }">
            <div class="flex items-center gap-3">
                <span class="font-medium">
                    {{ row.original.source_account_name }}
                </span>

                <UIcon name="i-lucide-arrow-right" class="text-gray-400 shrink-0" />

                <span class="font-medium">
                    {{ row.original.destination_account_name }}
                </span>
            </div>
        </template>

        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>

        <template #updated_by_name-cell="{ row }">
            <UTooltip :content="{ side: 'right', sideOffset: 8 }" :ui="{
                content: 'p-3 h-auto min-h-fit overflow-visible'
            }">
                <!-- Trigger -->
                <span class="cursor-help border-b border-dashed border-gray-400">
                    {{ row.original.updated_by_name || '—' }}
                </span>

                <template #content>
                    <div class="flex flex-col gap-3 text-sm">
                        <div>
                            <p class="text-gray-400">Created By</p>
                            <p>{{ row.original.created_by_name }}</p>
                        </div>

                        <div>
                            <p class="text-gray-400">Last Updated By</p>
                            <p>{{ row.original.updated_by_name || '—' }}</p>
                        </div>

                        <div>
                            <p class="text-gray-400">Voided By</p>
                            <p>{{ row.original.voided_by_name || '—' }}</p>
                        </div>
                    </div>
                </template>
            </UTooltip>
        </template>
    </UTable>
</template>