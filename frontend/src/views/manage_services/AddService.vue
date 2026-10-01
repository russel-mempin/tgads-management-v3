<script setup lang="ts">
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { PRICING_STRATEGIES, PRICE_UNITS } from '@/utils/constants';
import { z } from 'zod';
import { createService } from '@/api/services';
import ServiceOptionFormTable from '@/components/ServiceOptionFormTable.vue';

const toast = useToast()
const router = useRouter()

const tierSchema = z.object({
    min_threshold: z.number().min(0.1, 'Min threshold must be higher than 0'),
    max_threshold: z.number().min(0.1, 'Max threshold must be higher than 0'),
    rate: z.number().min(0.1, 'Rate must be higher than 0'),
})
const schema = z.object({
    name: z.string().min(1, 'Service name is required'),
    abbreviation: z.string().min(1, 'Service abbreviation is required'),
    pricing_strategy: z.enum(Object.values(PRICING_STRATEGIES), 'Pricing strategy is required'),
    unit: z.enum(Object.values(PRICE_UNITS), 'Unit is required'),
    options: z.array(
        z.object({
            name: z.string().min(1, 'Option name is required'),
            base_rate: z.number().min(0.1, 'Base rate must be higher than 0'),
            minimum_consumption: z.number().optional(),
            stock_increment: z.number().optional(),
            price_tiers: z.array(tierSchema).superRefine((tiers, ctx) => {
                if (!tiers) return
                tiers.forEach((tier, index) => {
                    // Min must be less than max
                    if (tier.min_threshold >= tier.max_threshold) {
                        ctx.addIssue({
                            code: 'custom',
                            message: 'Min threshold must be lower than max threshold',
                            path: [index, 'min_threshold'],
                        })
                    }
                    // Max must be less than the next tier's min
                    const nextTier = tiers[index + 1]
                    if (nextTier && tier.max_threshold >= nextTier.min_threshold) {
                        ctx.addIssue({
                            code: 'custom',
                            message: 'Max threshold must be lower than the next tier\'s min threshold',
                            path: [index, 'max_threshold'],
                        })
                    }
                })
            })
        })
    )
})
export type Schema = z.output<typeof schema>
const getInitialState = (): Schema => ({
    name: '',
    abbreviation: '',
    pricing_strategy: 'Fixed',
    unit: 'pcs',
    options: [{
        name: '',
        base_rate: 1,
        minimum_consumption: 0,
        stock_increment: 0,
        price_tiers: []
    }]
})
const state = reactive<Schema>(getInitialState())

const onSubmit = async () => {
    try {
        await createService(state)
        toast.add({
            title: 'Service created.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await router.push('/manage-services')
    }
    catch (error: any) {
        console.error('Error creating service:', error)
        toast.add({
            title: 'Failed to Save',
            description: error.response?.data?.detail
                ?? error.message
                ?? 'An unexpected error occurred.',
            color: 'error',
            icon: 'i-lucide-circle-x'
        })
    }
}
</script>

<template>
    <section class="m-8">
        <div class="flex items-start justify-between">
            <div>
                <p class="text-xs font-semibold uppercase tracking-widest text-primary mb-1">New Entry</p>
                <h1 class="text-2xl font-bold text-highlighted">Add Service</h1>
                <p class="text-sm text-muted mt-1">
                    Fields marked <span class="text-error font-semibold">*</span> are required.
                </p>
            </div>
        </div>
    </section>
    <UForm :schema="schema" v-model:state="state" @submit="onSubmit">
        <section class="bg-default border border-default rounded-md m-8">
            <div class="flex items-center gap-2 border-b border-default p-6">
                <UIcon name="i-lucide-concierge-bell"
                    class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <h2 class="font-semibold text-highlighted">Service Info</h2>
            </div>
            <div class="grid grid-cols-[3fr_1fr_1fr_1fr] divide-x divide-default">
                <UFormField label="Name" name="name" required class="flex-1 px-6 py-4">
                    <UInput v-model="state.name" type="text" placeholder="e.g. Tarpaulin" class="w-full" />
                </UFormField>
                <UFormField label="Abbreviation" name="abbreviation" required class="px-6 py-4">
                    <UInput v-model="state.abbreviation" type="text" placeholder="e.g. TARP" class="w-full" />
                </UFormField>
                <UFormField label="Pricing Strategy" name="pricing_strategy" required class="px-6 py-4">
                    <USelect v-model="state.pricing_strategy" :items="Object.values(PRICING_STRATEGIES)"
                        class="w-full" />
                </UFormField>
                <UFormField label="Unit" name="unit" required class="px-6 py-4">
                    <USelect v-model="state.unit" :items="Object.values(PRICE_UNITS)" class="w-full" />
                </UFormField>
            </div>
        </section>
        <ServiceOptionFormTable v-model="state.options" />
        <div class="sticky bottom-0 px-8 py-4 w-full shrink-0 border-t border-default backdrop-blur bg-default/60">
            <div class="flex gap-8 items-center justify-end">
                <UButton icon="i-lucide-arrow-left" color="neutral" class="w-45 font-bold" variant="outline">
                    Back to Services
                </UButton>
                <UButton class="w-45 font-bold relative" type="submit" loading-auto>
                    <template #leading>
                        <UIcon name="i-lucide-save" class="absolute left-3 size-5" />
                    </template>
                    <span class="w-full text-center">Save</span>
                </UButton>
            </div>
        </div>
    </UForm>
</template>