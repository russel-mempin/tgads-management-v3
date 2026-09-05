interface MiscSaleBase {
    date: string
    description: string
    reference_number?: string
    account_id: string
}

export interface MiscSale extends MiscSaleBase {
    id: string
    amount: string
    account_name: string
}

export interface MiscSaleCreate extends MiscSaleBase {
    amount: number
}

export interface MiscSaleUpdate {
    date?: string
    description?: string
    reference_number?: string | null
    amount?: number
    account_id?: string
}