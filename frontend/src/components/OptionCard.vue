<script setup lang="ts">
import { resolveComponent, h } from 'vue';
import { formatCurrency } from '@/utils/formatters';
import type { ServiceOption, ServicePriceTier } from '@/types/service';
import type { TableColumn } from '@nuxt/ui';

const UButton = resolveComponent('UButton')

const props = defineProps<{
    option: ServiceOption
    serviceUnit?: string
}>()

const emit = defineEmits<{
    editOption: [option: ServiceOption]
    deleteOption: [option: ServiceOption]
}>()

const columns: TableColumn<ServicePriceTier>[] = [
    {
        accessorKey: 'consumption',
        header: `Consumption (${props.serviceUnit})`,
        cell: ({ row }) => {
            const tier = row.original
            return tier.max_threshold
                ? `${tier.min_threshold} - ${tier.max_threshold}`
                : `${tier.min_threshold} UP`
        }
    },
    {
        accessorKey: 'rate',
        header: 'Rate',
        cell: ({ row }) => formatCurrency(row.original.rate)
    },
    {
        id: 'actions',
        header: '',
        cell: ({ row }) => h('div', { class: 'flex justify-end gap-1' }, [
            h(UButton, { variant: 'ghost', icon: 'i-lucide-pen-square' }),
            h(UButton, { variant: 'ghost', icon: 'i-lucide-trash-2', color: 'error' })
        ])
    }
]
</script>

<template>
    <div class="rounded-md border border-default bg-default">
        <div class="p-4 border-b border-default flex items-center justify-between">
            <div>
                <span class="flex items-center gap-2">
                    <p class="font-semibold">{{ option.name }}</p>
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
                </span>
                <p class="text-muted text-sm">{{ option.full_service_name }}</p>
            </div>
            <div class="flex gap-2 items-center">
                <p class="text-xl font-semibold" :class="option.is_priced ? 'text-green-700' : 'text-red-700'">{{ formatCurrency(option.base_rate) }}</p>
                <div class="flex items-center">
                    <UButton icon="i-lucide-pen-square" variant="ghost" @click="$emit('editOption', option)" />
                    <UButton icon="i-lucide-trash-2" variant="ghost" color="error" @click="$emit('deleteOption', option)" />
                </div>
            </div>ex
        </div>
        <UTable v-if="option.price_tiers?.length" :data="option.price_tiers" :columns="columns" />
        <div v-else class="p-4 flex items-center justify-between">
            <p class="text-sm text-muted">No tiered pricing - flat base rate applies
                at all quantities/consumption</p>
            <UButton label="Add Pricing Tier" icon="i-lucide-plus" variant="ghost" />
        </div>
    </div>
</template>