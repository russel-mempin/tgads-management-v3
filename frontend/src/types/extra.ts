interface ExtraBase {
	name: string
	price: number
	is_active: boolean
}

export interface Extra extends ExtraBase {
	id?: string
}

export type ExtraCreate = ExtraBase

export interface ExtraUpdate {
	name?: string
	price?: number
	is_active?: boolean
}