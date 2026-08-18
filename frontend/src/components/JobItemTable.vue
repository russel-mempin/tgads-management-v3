<script setup lang="ts">
import { ref, resolveComponent, h, computed } from 'vue'
import { formatCurrency, formatDate, getJobStatusColor } from '@/utils/formatters';
import type { JobItem, JobItemCreate } from '@/types/jobOrder';
import type { TableColumn } from '@nuxt/ui';

const toast = useToast()
const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')

const props = defineProps<{
    jobItems?: JobItem[]
    canCallApi: boolean
    joNumber?: number
}>()
const emit = defineEmits<{
    updated: []
    added: []
    addJobItem: [item: JobItemCreate]
    updateJobItem: [item: JobItemCreate]
    removeJobItem: [item_id: string]
}>()

// UI Variables
const isAddJobItemOpen = ref(false)
const isEditJobItemOpen = ref(false)
const selectedJobItem = ref<JobItem>()
const currentItemIds = computed(() => 
    props.jobItems?.map(item => item.item_id)
)

const openEditJobItem = (item: JobItem) => {
    selectedJobItem.value = item
    isEditJobItemOpen.value = true
}
const handleJobItemUpdated = async () => {
    emit('updated')
    toast.add({
        title: 'Changes Saved',
        description: 'Job Item information updated.',
        color: 'success',
    })
}
const handleJobItemAdded = async () => {
    emit('added')
    toast.add({
        title: 'New Item Saved',
        description: 'Job Item added.',
        color: 'success',
    })
}
const handleAddOrUpdateJobItem = (item: Omit<JobItemCreate, 'item_id'> & { item_id?: string }) => {
    console.log(item)
    // if (item.item_id) {
    //     // Editing an existing item — item_id already present
    //     emit('updateJobItem', item)
    // } else {
    //     emit('addJobItem', item)
    // }
    // itemPendingEdit.value = null
}

// Table data
const columns: TableColumn<JobItem>[] = [
    { accessorKey: 'item_id', header: 'ID' },
    {
        accessorKey: 'service_name_snapshot',
        header: 'Service',
        cell: ({ row }) => {
            const item = row.original

            if (!item.service_name_snapshot) {
                return '—'
            }

            const tooltipParts = [
                item.description ? `Description: ${item.description}` : '',
                item.notes ? `Notes: ${item.notes}` : '',
                ...(item.extras ?? []).map(
                    extra => `${extra.name_snapshot} (${extra.quantity}×)`
                )
            ].filter(Boolean)

            const serviceContent = h('div', {
                class: 'flex items-center gap-1 whitespace-nowrap'
            }, [
                h('span', {}, item.service_name_snapshot),

                item.service_option_name_snapshot
                    ? h(
                        'span',
                        { class: 'text-muted' },
                        `— ${item.service_option_name_snapshot}`
                    )
                    : null
            ])

            if (!tooltipParts.length) {
                return serviceContent
            }

            return h(
                resolveComponent('UTooltip'),
                {
                    text: tooltipParts.join('\n'),
                },
                {
                    default: () => serviceContent
                }
            )
        }
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
        accessorKey: 'quantity',
        header: 'Qty',
        cell: ({ row }) => `${row.original.quantity} pc(s)`
    },
    {
        accessorKey: 'unit_price',
        header: 'Unit Price',
        cell: ({ row }) => `${formatCurrency(row.original.unit_price)}`,
    },
    {
        accessorKey: 'subtotal',
        header: 'Subtotal',
        cell: ({ row }) => h('span', { class: 'font-semibold' }, formatCurrency(row.original.subtotal)),
    },
    { accessorKey: 'due_date', header: 'Due Date', cell: ({ row }) => `${formatDate(row.original.due_date)}`, },
    {
        accessorKey: 'total_claimed',
        header: 'Claimed',
        cell: ({ row }) =>
            `${row.original.total_claimed} / ${row.original.quantity}`
    },
    {
        accessorKey: 'job_status',
        header: 'Status',
        cell: ({ row }) => {
            return h(UBadge, { class: 'capitalize font-semibold', variant: 'solid', color: getJobStatusColor(row.original.job_status) }, () =>
                row.getValue('job_status')
            )
        }
    },
    {
        id: 'actions',
        header: `${props.canCallApi ? '' : 'Actions'}`,
        cell: ({ row }) => {
            if (props.canCallApi) {
                return h(UButton, {
                    color: 'info',
                    variant: 'outline',
                    icon: 'i-lucide-pen-square',
                    onClick: (e: Event) => {
                        e.stopPropagation()
                        console.log(row.original)
                        openEditJobItem(row.original)
                    }
                })
            }
        }
    }
]
</script>

<template>
    <EditJobItemForm v-model:isOpen="isEditJobItemOpen" :job-item="selectedJobItem" @updated="handleJobItemUpdated" />
    <JobItemForm 
        v-model:isOpen="isAddJobItemOpen" 
        :can-call-api="canCallApi" 
        :current-item-ids="currentItemIds" 
        :jo-number="props.joNumber" 
        @added="handleJobItemAdded" 
        @save="handleAddOrUpdateJobItem"
    />
    <section class="bg-default border border-default rounded-md">
        <div class="rounded-tl-md rounded-tr-md flex items-center justify-between p-4 border-b border-default">
            <div class="flex items-center gap-2">
                <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <h2 class="text-highlighted font-semibold">Job Items</h2>
            </div>
            <UButton @click="() => { isAddJobItemOpen = true }" icon="i-lucide-plus" label="Add Item"
                variant="outline" />
        </div>
        <UTable :data="props.jobItems" :columns="columns">
            <template #empty>
                <div class="flex flex-col items-center justify-center py-12 text-center px-6">
                    <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-3">
                        <UIcon name="i-lucide-package-open" class="size-6 text-muted" />
                    </div>
                    <p class="font-medium text-highlighted mb-1">No items yet</p>
                    <p class="text-sm text-muted">Click "Add Item" to start building this job order.</p>
                </div>
            </template>
        </UTable>
    </section>
</template>