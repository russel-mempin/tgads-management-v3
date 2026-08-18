<script setup lang="ts">
</script>

<template>
    <div class="border border-default rounded-md">
        <p class="bg-elevated p-4 border-b border-default rounded-tl-md rounded-tr-md uppercase font-bold text-sm">
            Pricing Breakdown</p>

        <div class="bg-muted border-b border-default px-4 py-2 grid"
            :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
            <p v-if="isAreaBased" class="uppercase text-sm">Consumption</p>
            <p v-if="isAreaBased" class="uppercase text-sm">Rate (Based on consumption)</p>
            <p class="uppercase text-sm">Unit Price</p>
            <p v-if="state.extraCharge != 0" class="uppercase text-sm">Extra Charge Total</p>
            <p class="uppercase text-sm">Extra Total</p>
            <p class="uppercase text-sm">Subtotal</p>
        </div>

        <div class="p-4 grid" :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
            <p v-if="isAreaBased">{{ `${pricingData?.consumption ?? 0} ${pricingData?.consumption_unit
                ?? state.unit}.` }}</p>
            <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
            <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
            <p v-if="state.extraCharge != 0">{{ `₱ ${extraChargeTotal}` }}</p>
            <p>{{ `₱ ${extraTotal}` }}</p>
            <p>₱ {{ subtotal }}</p>
        </div>
    </div>
</template>