interface TransferBase {
    reference_number: string
    transferred_at: string
    description: string
    source_account_id: string
    destination_account_id: string
}

export interface Transfer extends TransferBase {
    id: string
    amount: string
    created_at: string
    updated_at: string
    source_account_name: string
    destination_account_name: string

    created_by_name: string
    updated_by_name: string
    voided_by_name?: string
}

export interface TransferCreate extends TransferBase {
    amount: number
}

export interface TransferUpdate {
    reference_number?: string
    transferred_at?: string
    description?: string
    amount?: number
    source_account_id?: string
    destination_account_id?: string
}