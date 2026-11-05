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
    voided_by_name?: string
}

export interface TransferCreate {
    reference_number?: string
    description?: string
    amount: number
    transferred_at: string
    source_account_id: string
    destination_account_id: string
}