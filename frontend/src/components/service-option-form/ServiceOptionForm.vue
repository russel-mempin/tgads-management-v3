<script setup lang="ts">
import { reactive, watch } from 'vue'
import { z } from 'zod'
import type { ServiceOption, ServiceOptionCreate } from '@/types/service';
import OptionPriceTierFields from './OptionPriceTierFields.vue';

const props = defineProps<{
    parent_service_id: string,
    editingOption?: ServiceOption | null
}>()

const emit = defineEmits<{
    save: [option: ServiceOptionCreate]
    cancel: []
}>()

const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const schema = z.object({
    name: z.string().min(1, 'Name of the option is required.'),
    base_rate: z.number({ error: 'Base rate is required' }).positive('Value must be greater than 0'),
    minimum_consumption: z.number().optional(),
    stock_increment: z.number().optional(),
    pricing_tiers: z.array(
        z.object({
            min_threshold: z.number().int().positive(),
            max_threshold: z.number().int().positive().nullable(),
            rate: z.number().positive()
        })
    ),
})
type Schema = z.output<typeof schema>
const getInitialState = (): Schema => ({
    name: '',
    base_rate: 1,
    minimum_consumption: 0,
    stock_increment: 0,
    pricing_tiers: []
})
const state = reactive<Schema>(getInitialState())
const resetForm = () => {
    Object.assign(state, getInitialState())
}

watch([() => props.editingOption, isOpen], ([option, open]) => {
    if (open && option) {
        Object.assign(state, {
            name: option.name,
            base_rate: option.base_rate,
            minimum_consumption: option.minimum_consumption,
            stock_increment: option.stock_increment,
            pricing_tiers: option.price_tiers ?? []
        })
    }
    else {
        resetForm()
    }
})

const onSubmit = () => {
    emit('save', {
        name: state.name,
        base_rate: state.base_rate,
        minimum_consumption: state.minimum_consumption,
        stock_increment: state.stock_increment,
        price_tiers: state.pricing_tiers,
    })
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal :title="editingOption ? 'Edit Option' : 'Add Option'" v-model:open="isOpen"
        :close="{ color: 'error', class: 'rounded-full' }"
        description="Enter service option data to use it in job orders.">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-6" @submit="onSubmit">
                <UFormField label="Option Name" name="name" required class="w-full">
                    <UInput v-model="state.name" placeholder="Enter option name" class="w-full" />
                </UFormField>
                <div class="grid grid-cols-3 gap-4">
                    <UFormField label="Base Rate" name="base_rate" required class="w-full">
                        <UInputNumber v-model="state.base_rate" class="w-full" :increment="false" :decrement="false"
                            @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Min. Consumption" name="minimum_consumption" class="w-full">
                        <UInputNumber v-model="state.minimum_consumption" class="w-full" :increment="false"
                            :decrement="false" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Stock Increment" name="stock_increment" class="w-full">
                        <UInputNumber v-model="state.stock_increment" class="w-full" :increment="false"
                            :decrement="false" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                </div>
                <OptionPriceTierFields v-model:price-tiers="state.pricing_tiers" />
                <div class="flex justify-end gap-4">
                    <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg"
                        class="w-28" />
                    <UButton label="Save" icon="i-lucide-save" color="primary" size="lg" class="w-28 font-semibold"
                        type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>