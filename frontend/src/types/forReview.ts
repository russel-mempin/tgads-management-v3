import type { JobOrder } from "./jobOrder"

export type ReviewEntityType =
    | 'Job Order'
    | 'Payment'
    | 'Expense'
    | 'Misc Sale'

export type ReasonCategory =
    | 'Pricing Discrepancy'
    | 'Missing Data'
    | 'Status Issue'
    | 'Needs Verification'

export interface ForReview {
    id: string
    entity_type: ReviewEntityType
    entity_id: string
    entity_reference: string
    reason: string
    reason_category: ReasonCategory
    created_at: Date
    created_by_name: string
    resolved_at?: Date
    resolved_by_id?: string | null
    resolved_by_name?: string | null
}

export interface UnlinkedPayment {
    id: string
    date_received: string
    reference_number?: string | null
    amount: number
    customer_name?: string | null
    description?: string | null
    account_id: string
    account_name?: string | null
}

export interface PaymentForReview extends ForReview {
    entity: UnlinkedPayment
}