<script setup lang="ts">
import { computed, toRef } from 'vue';
import type { SizeUnit, JobItemExtraCreate } from '@/types/jobOrder';
import type { Extra } from '@/types/service';
import { useJobItemPricing } from '@/composables/jobItemPricing';

const props = defineProps<{
    selectedServiceId: string
    selectedOptionId: string
    extraList: Extra[]
    isAreaBased: boolean
}>()

const width = defineModel<number>('width')
const height = defineModel<number>('height')
const unit = defineModel<SizeUnit>('unit')
const quantity = defineModel<number>('quantity', { required: true })
const extras = defineModel<JobItemExtraCreate[]>('extras', { required: true })
const extraCharge = defineModel<number>('extraCharge', { required: true })
const discount = defineModel<number>('discount', { required: true })

const { pricingData } = useJobItemPricing(
    toRef(props, 'selectedServiceId'), toRef(props, 'selectedOptionId'),
    width, height, unit, quantity
)

const getExtraPrice = (extra: JobItemExtraCreate) => {
    const extraData = props.extraList.find(x => x.id === extra.extra_service_id)
    if (!extraData) return 0
    return extraData.price * extra.quantity
}
const extraTotal = computed(() =>
    extras.value.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const extraChargeTotal = computed(() =>
    extraCharge.value * quantity.value
)
const subtotal = computed(() =>
    ((pricingData.value?.unit_price ?? 0) * quantity.value) + extraTotal.value + extraChargeTotal.value - discount.value
)
</script>

<template>
    <slot name="breakdown" :pricing-data="pricingData" :extra-total="extraTotal" :extra-charge-total="extraChargeTotal"
        :subtotal="subtotal" />
</template>