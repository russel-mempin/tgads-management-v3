<script setup lang="ts">
const extraCharge = defineModel<number>('extraCharge', { required: true })
const discount = defineModel<number>('discount', { required: true })
</script>

<template>
    <div class="grid grid-cols-2 gap-6">
        <UFormField label="Extra Charge (Per Piece)" class="w-full">
            <UInputNumber v-model="extraCharge" :increment="false" :decrement="false"
                :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                class="w-full" :step="0.1" :step-snapping="false"
                @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
        </UFormField>
        <UFormField label="Discount (Flat)" class="w-full">
            <UInputNumber v-model="discount" :increment="false" :decrement="false"
                :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                class="w-full" :step="0.1" :step-snapping="false"
                @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
        </UFormField>
    </div>
</template>