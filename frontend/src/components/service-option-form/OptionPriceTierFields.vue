<script setup lang="ts">
import { ref } from 'vue';

const priceTiers = ref([
    {
        min_threshold: 1,
        max_threshold: null,
        rate: 1
    }
])

const addTier = () => {
    const previous = priceTiers.value.at(-1)
    priceTiers.value.push({
        min_threshold: previous?.max_threshold
            ? previous.max_threshold + 1
            : 1,
        max_threshold: null,
        rate: 1
    })
}

const removeTier = (index: number) => {
    priceTiers.value.splice(index, 1)
}

const updateNextMin = (index: number) => {
    const current = priceTiers.value[index]
    const next = priceTiers.value[index + 1]
    if (!current || !next || current.max_threshold == null) return
    next.min_threshold = current.max_threshold + 1
}
</script>

<template>
    <div class="border border-default bg-muted rounded-md">
        <div class="flex items-center justify-between p-4">
            <p class="uppercase font-bold">Pricing Tiers</p>
            <UButton label="Add Tier" @click="addTier" variant="subtle" icon="i-lucide-plus" :disabled="!priceTiers.length ||
                priceTiers[priceTiers.length - 1]?.max_threshold == null
                " />
        </div>
        <p v-if="!priceTiers.length" class="p-4 text-sm text-muted text-center">No pricing tiers added</p>
        <div v-for="(tier, index) in priceTiers" :key="index"
            class="grid grid-cols-[1fr_1fr_1fr_auto] gap-4 items-end p-4 border-b border-default last:border-b-0">
            <UFormField label="Min. Threshold" required>
                <UInputNumber v-model="tier.min_threshold" :min="1" :max="tier.max_threshold" :disabled="index > 0" class="w-full" />
            </UFormField>

            <UFormField label="Max. Threshold">
                <UInputNumber v-model="tier.max_threshold" :min="tier.min_threshold" class="w-full"
                    @update:model-value="updateNextMin(index)" />
            </UFormField>

            <UFormField label="Rate" required>
                <UInputNumber v-model="tier.rate" :min="1" class="w-full" :increment="false" :decrement="false"
                    :format-options="{
                        style: 'currency',
                        currency: 'PHP',
                        currencyDisplay: 'code',
                        currencySign: 'accounting'
                    }" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
            </UFormField>

            <UButton icon="i-lucide-trash-2" color="error" variant="ghost" @click="removeTier(index)" />
        </div>
    </div>
</template>