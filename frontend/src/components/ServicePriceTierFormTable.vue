<script setup lang="ts">
import type { Schema } from '@/views/manage_services/AddService.vue'
type PriceTier = NonNullable<Schema['options'][number]['price_tiers']>

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
    <div class="p-4">
        <div class="flex justify-between items-center mb-4">
            <h3 class="font-medium">Price Tiers</h3>
            <UButton type="button" label="Add Price Tier" icon="i-lucide-plus" size="sm" @click="addTier" />
        </div>

        <div v-for="(tier, index) in tiers" :key="index" class="flex gap-4 items-center mb-2">
            <UInputNumber v-model="tier.min_threshold" />
            <UInputNumber v-model="tier.max_threshold" />
            <UInputNumber v-model="tier.rate" />
            <UButton type="button" icon="i-lucide-x" color="error" variant="ghost" @click="removeTier(index)" />
        </div>
    </div>
</template>