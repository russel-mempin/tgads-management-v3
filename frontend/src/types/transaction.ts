import type { TRANSACTION_CATEGORIES } from "@/utils/constants"

export interface Transaction {
    date: string
    amount: string
    source_type: TRANSACTION_CATEGORIES,
    account_name: string
    description: string
}

export interface TransactionList {
    items: Transaction[]
    total: number
}