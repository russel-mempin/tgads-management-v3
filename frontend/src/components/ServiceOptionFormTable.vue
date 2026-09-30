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

const enableTiers = (index: number) => {
    options.value[index]!.price_tiers.push({
        min_threshold: 1,
        max_threshold: 10,
        rate: 1,
    })
}

const removeOption = (index: number) => {
    options.value.splice(index, 1)
}
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
        <div v-for="(option, index) in options" :key="index" class="border-b border-default last:border-b-0">
            <div class="flex p-6 gap-6">
                <UFormField label="Option Name" :name="`options.${index}.name`" class="flex-1" required>
                    <UInput v-model="option.name" placeholder="Option name" class="w-full" />
                </UFormField>
                <UFormField label="Base Rate" :name="`options.${index}.base_rate`" required>
                    <UInputNumber v-model="options[index]!.base_rate" :increment="false" :decrement="false"
                        @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" :step="0.01"
                        :format-options="{
                            style: 'currency',
                            currency: 'PHP',
                            currencyDisplay: 'code',
                            currencySign: 'accounting'
                        }"
                        class="w-full"
                    />
                </UFormField>
                <UFormField label="Minimum Consumption" :name="`options.${index}.minimum_consumption`">
                    <UInputNumber v-model="options[index]!.minimum_consumption" :min="0.1" :step="0.01" />
                </UFormField>
                <UFormField label="Stock Increment" :name="`options.${index}.stock_increment`">
                    <UInputNumber v-model="options[index]!.stock_increment" :min="0.1" placeholder="Option name" />
                </UFormField>
                <UFormField label="&nbsp;" class="shrink-0">
                    <div class="flex items-center gap-4">
                        <UButton v-if="option.price_tiers.length === 0" class="w-36 justify-center" icon="i-lucide-layers-plus" label="Enable Tiers" variant="soft" @click="enableTiers(index)" />
                        <UButton class="w-36 justify-center" icon="i-lucide-x" label="Delete Option" variant="soft" color="error" @click="removeOption" />
                    </div>
                </UFormField>
            </div>
            <ServiceOptionPriceTierTable :option-name="option.name" v-model="option.price_tiers" />
        </div>
    </section>
</template>