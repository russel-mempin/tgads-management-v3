<script setup lang="ts">
import { ref, resolveComponent, h } from 'vue'
import type { TableColumn } from '@nuxt/ui';
import type { JobItemCreate } from '@/types/jobOrder.ts'
import JobItemForm from './JobItemForm.vue'
import { formatDate } from '@/utils/formatters.ts';

const isOpen = ref(false)
const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')

const props = defineProps<{
    joNumber: number
    jobItems: JobItemCreate[]
}>()

const emit = defineEmits<{
  addJobItem: [item: JobItemCreate]
  updateJobItem: [item: JobItemCreate]
  removeJobItem: [item_id: string]
}>()

// UI Variables
const itemPendingEdit = ref<JobItemCreate | null>(null)
const itemPendingDelete = ref<JobItemCreate | null>(null)
const isDeleteConfirmOpen = ref(false)

// Data functions
const generateItemId = (serviceAbbreviation: string): string => {
    const existingCount = props.jobItems.filter(
        item => item.item_id.includes(`-${serviceAbbreviation}-`)
    ).length
    return `${props.joNumber}-${serviceAbbreviation}-${existingCount + 1}`
}

const handleAddOrUpdateJobItem = (item: Omit<JobItemCreate, 'item_id'> & { item_id?: string }) => {
    if (item.item_id) {
        // Editing an existing item — item_id already present
        emit('updateJobItem', item as JobItemCreate)
    } else {
        const item_id = generateItemId(item.service_abbreviation_snapshot)
        emit('addJobItem', { ...item, item_id } satisfies JobItemCreate)
    }
    itemPendingEdit.value = null
}

// UI Functions
const hasExpandableContent = (item: JobItemCreate): boolean => {
    return (
        item.extras.length > 0 ||
        !!item.notes ||
        !!item.description ||
        !!item.extra_charge ||
        !!item.discount
    )
}

const openEditForm = (item: JobItemCreate) => {
    itemPendingEdit.value = item
    isOpen.value = true
}

const requestRemoveJobItem = (item: JobItemCreate) => {
    itemPendingDelete.value = item
    isDeleteConfirmOpen.value = true
}

const confirmRemoveJobItem = () => {
    if (!itemPendingDelete.value) return
    emit('removeJobItem', itemPendingDelete.value.item_id)
    isDeleteConfirmOpen.value = false
    itemPendingDelete.value = null
}

const cancelRemoveJobItem = () => {
    isDeleteConfirmOpen.value = false
    itemPendingDelete.value = null
}

// Table data
const columns: TableColumn<JobItemCreate>[] = [
    { accessorKey: 'item_id', header: 'ID' },
    {
        accessorKey: 'service_name_snapshot',
        header: 'Service',
        cell: ({ row }) => {
            const item = row.original
            return item.service_name_snapshot && item.service_option_name_snapshot
                ? `${item.service_name_snapshot} - ${item.service_option_name_snapshot}`
                : '—'
        }
    },
    {
        accessorKey: 'quantity',
        header: 'Qty',
        cell: ({ row }) => `${row.original.quantity} pc(s)`
    },
    {
        id: 'size',
        header: 'Size',
        cell: ({ row }) => {
            const item = row.original
            return item.width && item.height
                ? `${item.width} x ${item.height} ${item.size_unit ?? ''}`
                : '—'
        },
    },
    {
        accessorKey: 'unit_price',
        header: 'Unit Price',
        cell: ({ row }) => `₱ ${row.original.unit_price.toLocaleString()}`,
    },
    {
        accessorKey: 'subtotal',
        header: 'Subtotal',
        cell: ({ row }) => `₱ ${row.original.subtotal.toLocaleString()}`,
    },
    {
        accessorKey: 'job_status',
        header: 'Status',
        cell: ({ row }) => {
            const color = {
                'Pending': 'warning' as const,
                'For Layout': 'info' as const,
                'For Approval': 'primary' as const,
                'For Printing': 'primary' as const,
                'For Pickup': 'success' as const,
                'Released': 'neutral' as const,
            }[row.getValue('job_status') as string]

            return h(UBadge, { class: 'capitalize font-semibold', variant: 'soft', color }, () =>
                row.getValue('job_status')
            )
        }
    },
    { accessorKey: 'due_date', header: 'Due', cell: ({ row }) => `${formatDate(row.original.due_date)}`, },
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
                        openEditForm(row.original)
                    }
                }),
                h(UButton, {
                    icon: 'i-lucide-trash-2',
                    color: 'error',
                    variant: 'ghost',
                    size: 'md',
                    onClick: (e: Event) => {
                        e.stopPropagation()
                        requestRemoveJobItem(row.original)
                    },
                }),
            ])
    }
]
</script>

<template>
    <UModal v-model:open="isDeleteConfirmOpen" title="Delete Job Item?">
        <template #body>
            <p class="text-sm text-muted">
                Are you sure you want to delete
                <span class="font-semibold text-highlighted">{{ itemPendingDelete?.item_id }}</span>
                ({{ itemPendingDelete?.service_name_snapshot }})? This can't be undone.
            </p>
            <div class="flex justify-end gap-3 mt-6">
                <UButton label="Cancel" color="neutral" variant="outline" @click="cancelRemoveJobItem" />
                <UButton label="Delete" color="error" @click="confirmRemoveJobItem" />
            </div>
        </template>
    </UModal>
    <JobItemForm v-model:isOpen="isOpen" :editing-item="itemPendingEdit" @save="handleAddOrUpdateJobItem" />
    <div class="bg-default border border-default rounded-md p-6 m-8">
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-2">
                <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <p class="font-semibold text-highlighted">Job Items</p>
            </div>
            <UTooltip text="Input a JO Number first.">
                <UButton @click="() => { isOpen = true }" :disabled="!joNumber" label="Add Item" icon="i-lucide-plus" />
            </UTooltip>
        </div>
        <!-- Empty state -->
        <div v-if="!jobItems.length" class="flex flex-col items-center justify-center py-12 text-center px-6">
            <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-3">
                <UIcon name="i-lucide-package-open" class="size-6 text-muted" />
            </div>
            <p class="font-medium text-highlighted mb-1">No items yet</p>
            <p class="text-sm text-muted">Click "Add Item" to start building this job order.</p>
        </div>
        <UTable v-else :data="jobItems" :columns="columns" class="border border-default rounded-md"
            @select="(e, row) => { if (hasExpandableContent(row.original)) row.toggleExpanded() }">
            <template #expanded="{ row }">
                <div class="p-4 bg-elevated grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-xs uppercase text-muted font-semibold mb-1">Extras</p>
                        <p v-if="!row.original.extras.length" class="text-sm text-muted">None</p>
                        <ul v-else class="text-sm space-y-1">
                            <li v-for="extra in row.original.extras" :key="extra.extra_service_id">
                                {{ extra.name_snapshot }} × {{ extra.quantity }} — ₱ {{ extra.price_snapshot *
                                    extra.quantity }}
                            </li>
                        </ul>
                    </div>
                    <div>
                        <p class="text-xs uppercase text-muted font-semibold mb-1">Notes</p>
                        <p class="text-sm">{{ row.original.notes || '—' }}</p>
                    </div>
                    <div>
                        <p class="text-xs uppercase text-muted font-semibold mb-1">Description</p>
                        <p class="text-sm">{{ row.original.description || '—' }}</p>
                    </div>
                    <div v-if="row.original.extra_charge">
                        <p class="text-xs uppercase text-muted font-semibold mb-1">Extra Charge</p>
                        <p class="text-sm">{{ row.original.extra_charge }}</p>
                    </div>
                    <div v-if="row.original.discount">
                        <p class="text-xs uppercase text-muted font-semibold mb-1">Discount</p>
                        <p class="text-sm">{{ row.original.discount }}</p>
                    </div>
                </div>
            </template>
        </UTable>
    </div>
</template>