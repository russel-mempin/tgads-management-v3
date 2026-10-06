<script setup lang="ts">
import type { Schema } from '@/views/manage_services/AddService.vue'
type PriceTier = NonNullable<Schema['options'][number]['price_tiers']>

const props = defineProps<{
    optionName: string
}>()

const tiers = defineModel<PriceTier>({ required: true })

const addTier = () => {
    tiers.value.push({
        min_threshold: 1,
        max_threshold: 10,
        rate: 1,
    })
}

const removeTier = (index: number) => {
    tiers.value.splice(index, 1)
}
</script>

<template>
    <div v-if="tiers.length !== 0" class="px-6 pb-6">
        <div class="bg-default border border-default rounded-md">
            <div class="flex items-center justify-between px-6 py-4 border-b border-default">
                <p class="font-semibold">Price Tiers for {{ optionName }}</p>
                <UButton label="Add Tier" icon="i-lucide-plus" @click="addTier" variant="subtle" />
            </div>
            <div class="grid grid-cols-[3fr_1fr_1fr_1fr_0.2fr] gap-6 bg-muted border-b border-default px-6 py-2 uppercase text-muted font-semibold">
                <p>Tier No.</p>
                <p>Min. Threshold</p>
                <p>Max. Threshold</p>
                <p>Rate</p>
                <p></p>
            </div>
            <div v-for="(tier, index) in tiers" class="grid grid-cols-[3fr_1fr_1fr_1fr_0.2fr] gap-6 px-6 py-4 border-default border-b last:border-b-0">
                <p class="self-center">Tier No. {{ index + 1 }}</p>
                <UInputNumber v-model="tier.min_threshold" />
                <UInputNumber v-model="tier.max_threshold" />
                <UInputNumber v-model="tier.rate" 
                    :increment="false" 
                    :decrement="false"
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" 
                    :step="0.01"
                    :format-options="{
                        style: 'currency',
                        currency: 'PHP',
                        currencyDisplay: 'code',
                        currencySign: 'accounting'
                    }"
                />
                <UButton icon="i-lucide-x" variant="ghost" color="error" @click="() => { removeTier(index) }" />
            </div>
        </div>
    </div>
</template>