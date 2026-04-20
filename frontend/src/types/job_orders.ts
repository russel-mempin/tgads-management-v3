export interface JobItem {
	jo_number: string
	item_id: string
	description: string
	height: number
	width: number
	size_unit: string
	paper_size: string
	quantity: number
	job_status: string
	due_date: string
	discount: number
	unit_price: number
	subtotal: number
	total_claimed: number
	remaining_on_hand: number
	service_name: string
	extra_service_name: string
	extra_service_price: number
}

export interface Payment {
	date_received: string
	method: string
	amount: number
}

export interface ClaimingHistory {
	date_claimed: string
	name: string
	pcs_claimed: number
}

export interface JobOrder {
	id: string
	jo_number: string
	date_received: string
	override_payment_status: boolean
	job_items: JobItem[]
	payments: Payment[]
	claims: ClaimingHistory[]
	payment_status: string
	total_due: number
	total_paid: number
	customer_name: string
}
