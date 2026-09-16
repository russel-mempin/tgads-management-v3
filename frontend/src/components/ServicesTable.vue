<script setup lang="ts">
import { ref, h, resolveComponent } from 'vue'
import type { TableColumn, TableRow } from '@nuxt/ui'
import type { Service } from '@/types/service'
import { formatCurrency } from '@/utils/formatters';
import { useRouter } from 'vue-router';

const router = useRouter()
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')

const props = defineProps<{
    services: Service[]
}>()


const columns: TableColumn<Service>[] = [
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
        accessorKey: 'name',
        header: 'Name',
    },
    {
        accessorKey: 'abbreviation',
        header: 'Abbreviation',
    },
    {
        accessorKey: 'pricing_strategy',
        header: 'Pricing By',
    },
    {
        accessorKey: 'unit',
        header: 'Unit',
    },
    {
        accessorKey: 'actions',
        header: '',
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
                        router.push(`/manage-services/view/${row.original.id}`)
                    }
                }),
            ])
    },
]

const expanded = ref({})
const onSelect = (_e: Event, row: TableRow<Service>) => {
    row.toggleExpanded()
}
</script>

<template>
    <UTable v-model:expanded="expanded" :data="services" :columns="columns"
        :ui="{ tr: 'data-[expanded=true]:bg-elevated/50' }" class="flex-1" @select="onSelect">
        <template #expanded="{ row }">
            <div class="p-2">
                <p class="text-sm font-semibold text-muted uppercase mb-2">Options</p>
                <div v-if="row.original.options" class="border border-default rounded-md overflow-hidden bg-default">
                    <table class="w-full text-sm">
                        <thead class="bg-elevated">
                            <tr class="text-left text-muted uppercase">
                                <th class="p-2.5">Name</th>
                                <th class="p-2.5">Base Rate</th>
                                <th class="p-2.5">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="option in row.original.options" :key="option.id" class="border-t border-default">
                                <td class="p-2.5">{{ option.name }}</td>
                                <td class="p-2.5">{{ formatCurrency(option.base_rate) }}</td>
                                <td class="p-2.5">
                                    <span :class="[
                                        'flex items-center gap-1.5 font-medium',
                                        option.is_active ? 'text-green-700' : 'text-red-700'
                                    ]">
                                        <span :class="[
                                            'size-2 rounded-full',
                                            option.is_active ? 'bg-green-700' : 'bg-red-700'
                                        ]" />
                                        {{ option.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </template>
    </UTable>
</template>
