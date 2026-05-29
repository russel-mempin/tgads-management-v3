export interface ServiceType {
	name: string
	abbreviation: string
	price: number
	unit: string
	is_area_based: boolean
	required_measurement_unit: string
	id: string
}

export interface ServiceCreate {
	name: string
	abbreviation: string
	price: number
	unit: string
	is_area_based: boolean
	required_measurement_unit: string
}

export interface ExtraServiceCreate {
    name: string
    price: number
}

export interface ExtraService extends ExtraServiceCreate {
    id: string
}