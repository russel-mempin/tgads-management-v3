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
  due_date: Date
  discount: number
  unit_price: number
  subtotal: number
  total_claimed: number
  remaining_on_hand: number
  service_name: string
  extra_service_name: string
  extra_service_price: number
  notes: string
}

export interface JobItemCreate {
  jo_number: string
  item_id: string
  description: string
  height: number
  width: number
  size_unit: string
  paper_size: string
  quantity: number
  job_status: string
  due_date: Date
  discount: number
  notes: string
  service_type_id: string
  extra_type_id: string | null
  // display only
  service_name: string
  extra_service_name: string
  extra_service_price: number
  unit_price: number
}

export interface JobItemPayload {
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
  notes: string
  service_type_id: string
  extra_type_id: string | null
}

export interface Payment {
  date_received: string
  method: string
  amount: number
}

export interface PaymentCreate {
  date_received: Date
  method: string
  amount: number
}

export interface ClaimingHistory {
  date_claimed: string
  name: string
  pcs_claimed: number
  claimed_item_id: string
}

export interface ClaimCreate {
  date_claimed: Date
  name: string
  pcs_claimed: number
  claimed_item_id: string
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
  customer_email: string
  customer_contact_no: string
}

export interface JobOrderCreate {
  jo_number: string
  date_received: string
  override_payment_status?: string
  customer_id?: string
  customer_name?: string
  customer_address?: string
  customer_contact_no?: string
  customer_email?: string
  job_items: JobItemPayload[]
  payments?: Payment[]
  claims?: ClaimingHistory[]
}
