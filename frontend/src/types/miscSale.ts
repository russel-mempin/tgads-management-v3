interface MiscSaleBase {
    date: string
    description: string
    reference_number?: string
    account_id: string
}

export interface MiscSale extends MiscSaleBase {
    id: string
    amount: string
}

export interface MiscSaleCreate extends MiscSaleBase {
    amount: number
}