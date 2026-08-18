import { ref } from 'vue'
import type { PricingData } from '@/types/jobOrder'

export const useJobItemPricing = () => {
    const pricingData = ref<PricingData>()
    return pricingData
}

// let debounceTimer: ReturnType<typeof setTimeout>

// watch(
//     () => [state.width, state.height, state.quantity, state.selectedService, state.selectedOption, state.unit],
//     () => {
//         clearTimeout(debounceTimer)
//         debounceTimer = setTimeout(async () => {
//             if (!state.selectedService || !state.selectedOption || !state.quantity) return
//             if (isAreaBased.value && (!state.width || !state.height || !state.unit)) return

//             pricingData.value = await getUnitPrice({
//                 height: state.height ?? 0,
//                 width: state.width ?? 0,
//                 service_id: state.selectedService,
//                 option_id: state.selectedOption,
//                 size_unit: state.unit ?? 'ft.',
//                 quantity: state.quantity
//             })
//         }, 400)
//     }
// )