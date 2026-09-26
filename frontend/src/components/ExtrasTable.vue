<script setup lang="ts">
import { resolveComponent, h } from 'vue';
import type { Extra} from '@/types/extra';
import type { TableColumn } from '@nuxt/ui';
import { formatCurrency } from '@/utils/formatters';

const UButton = resolveComponent('UButton')

const props = defineProps<{
    extra: Extra[]
}>()

const columns: TableColumn<Extra>[] = [
    {
        accessorKey: 'name',
        header: 'Name',
    },
    {
        accessorKey: 'price',
        header: 'Price',
        cell: ({ row }) => `${formatCurrency(row.getValue('price'))}`
    },
    {
        accessorKey: 'is_active',
        header: 'Status',
        cell: ({ row }) => {
            const isActive = row.getValue('is_active') as boolean

            return h(
                'span',
                {
                    class: [
                        'flex items-center gap-1.5 font-medium',
                        isActive ? 'text-green-700' : 'text-red-700'
                    ]
                },
                [
                    h('span', {
                        class: [
                            'size-2 rounded-full',
                            isActive ? 'bg-green-700' : 'bg-red-700'
                        ]
                    }),
                    isActive ? 'Active' : 'Inactive'
                ]
            )
        }
    },
    {
        id: 'actions',
        header: '',
        cell: ({ row }) =>
            h('div', { class: 'flex items-center gap-2' }, [
                h(UButton, {
                    color: 'primary',
                    variant: 'ghost',
                    icon: 'i-lucide-pen-square',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        console.log("Test")
                    }
                }),
                h(UButton, {
                    color: 'error',
                    variant: 'ghost',
                    icon: 'i-lucide-trash-2',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        console.log("Test")
                    }
                }),
            ])
    }
]
</script>

<template>
    <UTable :data="extra" :columns="columns">
        <template #actions-cell="{ row }">
            <slot name="actions" :item="row.original" :index="row.index" />
        </template>
    </UTable>
</template>