interface JobItemCore {
  jo_number: number
  item_id: string
  description: string
  height: number
  width: number
  size_unit: string
  quantity: number
  job_status: string
  due_date: Date
  discount: number
  extra_charge: number
  notes: string
  service_name: string
  extra_service_name: string
}

export interface JobItemFromDB extends JobItemCore {
  subtotal: number
  total_claimed: number
  remaining_on_hand: number
}

export interface JobItemPayload extends JobItemCore {
  // Display only (Not saved in database)
  unit_price: number
  extra_service_price: number
}

export interface Payment {
  date_received: Date
  method: string
  amount: number
}

export interface ClaimingHistory {
  date_claimed: Date
  name: string
  pcs_claimed: number
  claimed_item_id: string
}

export interface JobOrder {
  id: string
  jo_number: number
  date_received: Date
  override_payment_status: boolean
  overall_job_status: string
  job_items: JobItemFromDB[]
  payments: Payment[]
  claims: ClaimingHistory[]
  payment_status: string
  total_due: number
  total_paid: number
  customer_name: string
  customer_email: string
  customer_contact_no: string
  created_at: Date
  updated_at: Date
  created_by_name: string
  updated_by_name: string
}

export interface JobOrderCreate {
  jo_number: number
  date_received: Date
  override_payment_status?: string
  customer_id?: string
  customer_name?: string
  customer_address?: string
  customer_contact_no?: string
  customer_email?: string
  job_items: JobItemCore[]
  payments?: Payment[]
  claims?: ClaimingHistory[]
}
