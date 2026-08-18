<script setup lang="ts">
import { computed } from 'vue';
import { useJobItemPricing } from '@/composables/jobItemPricing';
import type { SizeUnit, JobItemExtraCreate } from '@/types/jobOrder';
import type { Extra } from '@/types/service';

const props = defineProps<{ 
    extraList: Extra[]
    isAreaBased: boolean
}>()

const serviceId = defineModel<string>('serviceId', { required: true })
const serviceOptionId = defineModel<string>('serviceOptionId', { required: true })
const width = defineModel<number | undefined>('width')
const height = defineModel<number | undefined>('height')
const unit = defineModel<SizeUnit | undefined>('unit')
const quantity = defineModel<number>('quantity', { required: true })
const extraCharge = defineModel<number | undefined>('extraCharge')
const extras = defineModel<JobItemExtraCreate[] | undefined>('extras')
const breakdownColumns = computed(() => {
    let cols = 3
    if (props.isAreaBased) cols += 2
    if (extraCharge.value != 0) cols += 1
    return cols
})
const getExtraPrice = (extra: JobItemExtraCreate) => {
    const extraData = props.extraList.find(x => x.id === extra.extra_service_id)
    if (!extraData) return 0
    return extraData.price * extra.quantity
}
const { pricingData } = useJobItemPricing(
    serviceId,
    serviceOptionId,
    width,
    height,
    unit,
    quantity,
)
const extraTotal = computed(() =>
    extras.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const extraChargeTotal = computed(() =>
    extraCharge.value ?? 0 * quantity.value
)
const subtotal = computed(() =>
    ((pricingData.value?.unit_price ?? 0) * quantity.value) + extraTotal.value + extraChargeTotal.value - discount.value
)
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
            <p v-if="extraCharge != 0" class="uppercase text-sm">Extra Charge Total</p>
            <p class="uppercase text-sm">Extra Total</p>
            <p class="uppercase text-sm">Subtotal</p>
        </div>

        <div class="p-4 grid" :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
            <p v-if="isAreaBased">{{ `${pricingData?.consumption ?? 0} ${pricingData?.consumption_unit
                ?? unit}.` }}</p>
            <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
            <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
            <p v-if="extraCharge != 0">{{ `₱ ${extraCharge ?? 0 * quantity}` }}</p>
            <p>{{ `₱ ${extraTotal}` }}</p>
            <p>₱ {{ subtotal }}</p>
        </div>
    </div>
</template>