export interface ServiceType {
	name: string
	abbreviation: string
	price: number
	unit: string
	is_area_based: boolean
	id: string
}

export interface ServiceCreate {
	name: string
	abbreviation: string
	price: number
	unit: string
	is_area_based: boolean
}

export interface ExtraServiceCreate {
    name: string
    price: number
}

export interface ExtraService extends ExtraServiceCreate {
    id: string
}