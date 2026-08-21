import { computed, type Ref } from 'vue'
import type { JobItemTableRow, Payment, ClaimingHistory } from '@/types/jobOrder'

export function useJobOrderTotals(
  joNumber: Ref<number>,
  jobItems: Ref<JobItemTableRow[]>,
  payments: Ref<Payment[]>,
  claimingHistory: Ref<ClaimingHistory[]>,
) {
  const totalDue = computed(() => jobItems.value.reduce((sum, item) => sum + item.subtotal, 0))

  const totalPaid = computed(() => payments.value.reduce((sum, item) => sum + item.amount, 0))

  const balance = computed(() => totalDue.value - totalPaid.value)

  // Map of job_item_id -> total pcs claimed
  const totalClaimedByItem = computed(() => {
    const map = new Map<string, number>()
    for (const claim of claimingHistory.value) {
      const current = map.get(claim.claimed_item_id) ?? 0
      map.set(claim.claimed_item_id, current + claim.pcs_claimed)
    }
    return map
  })

  const getTotalClaimed = (itemId: string) => totalClaimedByItem.value.get(itemId) ?? 0

  const hasValidJoNumber = computed(() => joNumber.value > 0)

  const hasJobItems = computed(() => jobItems.value.length > 0)

  const hasValidPayments = computed(() => payments.value.every((payment) => payment.amount > 0))

  const hasValidClaims = computed(() =>
    claimingHistory.value.every(
      (claim) => claim.claimed_item_id && claim.pcs_claimed > 0 && claim.date_claimed,
    ),
  )

  const canSave = computed(
    () =>
      hasValidJoNumber.value && hasJobItems.value && hasValidPayments.value && hasValidClaims.value,
  )

  return {
    totalDue,
    totalPaid,
    balance,
    totalClaimedByItem,
    getTotalClaimed,
    hasValidJoNumber,
    hasJobItems,
    hasValidPayments,
    hasValidClaims,
    canSave,
  }
}
