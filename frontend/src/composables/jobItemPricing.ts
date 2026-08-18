import { ref, watch, type Ref } from 'vue'
import type { PricingData, SizeUnit } from '@/types/jobOrder'
import { getUnitPrice } from '@/api/jobOrders'

export const useJobItemPricing = (
    serviceId: Ref<string>,
    serviceOptionId: Ref<string>,
    width: Ref<number | undefined>,
    height: Ref<number | undefined>,
    unit: Ref<SizeUnit | undefined>,
    quantity: Ref<number>,
) => {
    const pricingData = ref<PricingData>()
    let debounceTimer: ReturnType<typeof setTimeout>

    watch(
        [
            serviceId,
            serviceOptionId,
            width,
            height,
            quantity,
            unit
        ],
        () => {
            clearTimeout(debounceTimer)
            debounceTimer = setTimeout(async () => {
                if (!serviceId.value || !serviceOptionId.value || !quantity.value) {
                    return
                }
                if (!width.value || !height.value || !unit.value) {
                    return
                }
                pricingData.value = await getUnitPrice({
                    height: height.value ?? 0,
                    width: width.value ?? 0,
                    service_id: serviceId.value,
                    option_id: serviceOptionId.value,
                    size_unit: unit.value ?? 'ft.',
                    quantity: quantity.value
                })
            }, 400)
        }
    )

    return {
        pricingData
    }
}