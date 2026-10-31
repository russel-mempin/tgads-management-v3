export interface Transfer {
    reference_number?: string
    description?: string
    amount: string
    transferred_at: string
    created_at: string
    updated_at: string
    source_account_name: string
    destination_account_name: string
    created_by_name: string
    updated_by_name: string
}