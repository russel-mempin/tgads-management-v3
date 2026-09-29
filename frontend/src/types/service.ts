import type { PriceUnit, PricingStrategy } from '@/utils/constants'

interface ServiceBase {
	name: string
	abbreviation: string
	pricing_strategy: string
	unit: string
	is_active: boolean
}

export interface ServicePriceTier {
	id?: string
	min_threshold: number
	max_threshold?: number | null
	rate: number
}

export interface ServiceOption {
	id: string
	name: string
	option_name: string
	base_rate: number
	minimum_consumption: number
	stock_increment: number
	price_tiers?: ServicePriceTier[]
	full_service_name: string
	is_active: boolean
	is_priced: boolean
}

export interface Service extends ServiceBase {
	created_at?: Date
	updated_at?: Date
	id?: string
	options: ServiceOption[]
}

export interface ServiceBaseEdit {
	name?: string
	abbreviation?: string
	pricing_strategy?: PricingStrategy
	unit?: PriceUnit
	is_active?: boolean
}

export interface ServiceOptionCreate {
	name: string
	base_rate: number
	minimum_consumption?: number
	stock_increment?: number
	price_tiers: ServicePriceTier[]
}

export type ServiceOptionUpdate = Partial<ServiceOptionCreate>