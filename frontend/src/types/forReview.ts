export interface ForReview {
    id: string
    entity_type: string
    entity_id: string
    entity_reference: string
    reason: string
    created_at: Date
    created_by_name: string
    resolved_at?: Date
    resolved_by_id?: Date
}