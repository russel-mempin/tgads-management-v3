<script setup lang="ts">
import { reactive } from 'vue';
import { z } from 'zod';
import { PRICING_STRATEGIES, PRICE_UNITS } from '@/utils/constants';
import type { Service, ServiceBaseEdit } from '@/types/service';

const isOpen = defineModel<boolean>('isOpen', { required: true })

const props = defineProps<{
    serviceData?: Service
}>()

const schema = z.object({
    name: z.string().min(1, 'Name is required'),
    abbreviation: z.string().min(1, 'Name is required'),
    pricing_strategy: z.enum(PRICING_STRATEGIES, { error: 'Pricing strategy is required' }),
    unit: z.enum(PRICE_UNITS, { error: 'Unit is required' }),
    is_active: z.string().min(1, 'Name is required'),
})
type Schema = z.output<typeof schema>
const getInitialState = (): Schema => ({
    name: '',
    abbreviation: '',
    pricing_strategy: 'Fixed',
    unit: 'pcs',
    is_active: 'true',
})
const state = reactive<Schema>(getInitialState())

// Initialize state with service data if provided
if (props.serviceData) {
    console.log(props.serviceData)
    Object.assign(state, props.serviceData)
}

const handleCancel = () => {
    console.log("Cancel")
}
const onSubmit = () => {
    console.log("Hi")
}
</script>

<template>
    <UModal title="Edit Service Info" v-model:open="isOpen" description="Change information of the base service."
        :close="{ color: 'error', class: 'rounded-full' }">
        <template #body>
            <UForm :schema="schema" v-model:state="state" @submit="onSubmit">
                <UFormField label="Name">
                    <UInput v-model="state.name" class="w-full" placeholder="Tarpaulin" />
                </UFormField>
                <UFormField label="Abbreviation" class="mt-6">
                    <UInput v-model="state.abbreviation" class="w-full" placeholder="TARP" />
                </UFormField>
                <div class="grid grid-cols-2 gap-6 mt-6">
                    <UFormField label="Pricing Strategy">
                        <USelect v-model="state.pricing_strategy" class="w-full" />
                    </UFormField>
                    <UFormField label="Unit">
                        <USelect v-model="state.unit" class="w-full" placeholder="TARP" />
                    </UFormField>
                </div>
                <div class="flex justify-end gap-6 mt-6">
                    <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg"
                        class="w-28 justify-center" @click="handleCancel" />
                    <UButton label="Save" icon="i-lucide-save" color="primary" size="lg"
                        class="w-28 font-semibold justify-center items-center" type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>