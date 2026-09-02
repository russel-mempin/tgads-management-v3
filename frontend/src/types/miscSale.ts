export interface MiscSale {
    date: string
    description: string
    amount: string
    is_archived: boolean
    reference_number: string
    id: string
    account_id: string
}

export interface MiscSaleCreate {
    date: string
    description: string
    amount: number
}