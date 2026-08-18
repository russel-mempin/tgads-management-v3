interface ServicePriceTier {
	min_threshold: number
	max_threshold: number
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
}

export interface Service {
	name: string
	abbreviation: string
	pricing_strategy: string
	unit: string
	is_active: boolean
	created_at?: Date
	updated_at?: Date
	id?: string
	options: ServiceOption[]
}

export interface Extra {
	id?: string
	name: string
	price: number
	is_active: boolean
	created_at?: Date
	updated_at?: Date
}