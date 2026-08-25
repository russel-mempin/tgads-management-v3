import type { JobOrder, JobItem } from "./jobOrder"

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

export interface PossibleMatches {
    id: string
    jo_number: number
    job_items: JobItem[]
    customer_name?: string
    date_received: Date
    total_due: number
    total_paid: number
    remaining_balance: number
    match_score: number
    match_reasons: string[]
}

export interface UnlinkedPayment {
    id: string
    date_received: Date
    reference_number?: string | null
    amount: number
    customer_name?: string | null
    description?: string | null
    account_id: string
    account_name?: string | null
    possible_matches: PossibleMatches[]
}

export interface PaymentForReview extends ForReview {
    entity: UnlinkedPayment
}