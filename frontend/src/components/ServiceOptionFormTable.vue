<script setup lang="ts">
import { resolveComponent, h, ref } from 'vue';
import type { TableColumn } from '@nuxt/ui'
import type { Schema } from '@/views/manage_services/AddService.vue';
import ServiceOptionPriceTierTable from '@/components/ServicePriceTierFormTable.vue'

const options = defineModel<Schema['options']>({ required: true })

const UButton = resolveComponent('UButton')

const addOption = () => {
    options.value.push({
        name: '',
        base_rate: 1,
        minimum_consumption: 0,
        stock_increment: 0,
        price_tiers: []
    })
}

const removeOption = (index: number) => {
    options.value.splice(index, 1)
}

const expanded = ref({})

const columns: TableColumn<Schema['options'][number]>[] = [
    {
        accessorKey: 'name',
        header: 'Name',
    },
    {
        accessorKey: 'base_rate',
        header: 'Base Rate',
    },
    {
        accessorKey: 'minimum_consumption',
        header: 'Minimum Consumption',
    },
    {
        accessorKey: 'stock_increment',
        header: 'Stock Increment',
    },
    {
        id: 'actions',
        header: '',
        cell: ({ row }) =>
            h('div', { class: 'flex items-center gap-2' }, [
                h(UButton, {
                    color: 'neutral',
                    variant: 'ghost',
                    icon: 'i-lucide-chevron-down',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        row.toggleExpanded()
                    }
                }),
                h(UButton, {
                    color: 'error',
                    variant: 'ghost',
                    icon: 'i-lucide-x',
                    size: 'md',
                    onClick: (event: Event) => {
                        event.stopPropagation()
                        removeOption(row.index)
                    }
                }),
            ])
    }
]
</script>
<template>
    <section class="bg-default border border-default rounded-md m-8">
        <div class="flex justify-between items-center p-6 border-b border-default">
            <div class="flex items-center gap-2">
                <UIcon name="i-lucide-settings-2" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <h2 class="font-semibold text-highlighted">Options</h2>
            </div>
            <UButton type="button" label="Add Option" @click="addOption" icon="i-lucide-plus" />
        </div>
        <UTable v-model:expanded="expanded" :data="options" :columns="columns">
            <template #name-cell="{ row }">
                <UFormField :name="`options.${row.index}.name`" required>
                    <UInput v-model="options[row.index]!.name" placeholder="Option name" />
                </UFormField>
            </template>
            <template #base_rate-cell="{ row }">
                <UFormField :name="`options.${row.index}.base_rate`" required>
                    <UInputNumber v-model="options[row.index]!.base_rate" :increment="false" :decrement="false"
                        @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" :step="0.01"
                        :format-options="{
                            style: 'currency',
                            currency: 'PHP',
                            currencyDisplay: 'code',
                            currencySign: 'accounting'
                        }" />
                </UFormField>
            </template>
            <template #minimum_consumption-cell="{ row }">
                <UFormField :name="`options.${row.index}.minimum_consumption`">
                    <UInputNumber v-model="options[row.index]!.minimum_consumption" :step="0.01" />
                </UFormField>
            </template>
            <template #stock_increment-cell="{ row }">
                <UFormField :name="`options.${row.index}.stock_increment`">
                    <UInputNumber v-model="options[row.index]!.stock_increment" placeholder="Option name" />
                </UFormField>
            </template>
            <template #expanded="{ row }">
                <ServiceOptionPriceTierTable v-model="options[row.index]!.price_tiers" />
            </template>
        </UTable>
    </section>
</template>