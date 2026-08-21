// composables/useJobItemBuilder.ts
import type { Ref } from 'vue'
import type { JobItemCreate, JobItemTableRow, JobItemExtra } from '@/types/jobOrder'
import type { Service, Extra } from '@/types/service'

export function useJobItemBuilder(
  serviceList: Ref<Service[]>,
  extraList: Ref<Extra[]>,
  getUnitPrice: (params: {
    height: number
    width: number
    service_id: string
    option_id: string
    size_unit: string
    quantity: number
  }) => Promise<{ unit_price: number }>,
) {
  const resolveServiceId = (name: string): string | undefined =>
    serviceList.value.find((s) => s.name === name)?.id

  const resolveOptionId = (serviceName: string, optionName: string): string | undefined =>
    serviceList.value.find((s) => s.id === serviceName)?.options.find((o) => o.name === optionName)
      ?.id

  const buildJobItem = async (item: JobItemCreate): Promise<JobItemTableRow> => {
    const service = serviceList.value.find((s) => s.id === item.service_id)
    const option = service?.options.find((o) => o.id === item.service_option_id)

    const pricingData = await getUnitPrice({
      height: item.height ?? 0,
      width: item.width ?? 0,
      service_id: item.service_id,
      option_id: item.service_option_id,
      size_unit: item.size_unit!,
      quantity: item.quantity,
    })

    const extras: JobItemExtra[] = item.extras.map((e) => {
      const extra = extraList.value.find((x) => x.id === e.extra_service_id)
      return {
        extra_service_id: e.extra_service_id,
        quantity: e.quantity,
        name_snapshot: extra?.name ?? 'Unknown Extra',
        price_snapshot: extra?.price ?? 0,
      }
    })

    const extraTotal = extras.reduce((sum, e) => sum + e.price_snapshot * e.quantity, 0)
    const extraChargeTotal = item.extra_charge * item.quantity

    const subtotal =
      pricingData.unit_price * item.quantity + extraTotal + extraChargeTotal - item.discount_amount

    return {
      ...item,
      unit_price: pricingData.unit_price,
      subtotal,
      service_name_snapshot: service?.name ?? '-',
      service_option_name_snapshot: option?.name ?? '-',
      total_claimed: 0,
      remaining_on_hand: item.quantity,
      extras,
    }
  }

  return { buildJobItem, resolveServiceId, resolveOptionId }
}
