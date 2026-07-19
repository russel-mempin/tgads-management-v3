interface JobItemExtra {
  id: string
  extra_service_id: string
  quantity: number
  price_snapshot: number
  name_snapshot: string
}

export interface JobItem {
  item_id: string
  description: string
  height: number
  width: number
  size_unit: string
  quantity: number
  job_status: string
  due_date: Date
  notes: string
  unit_price: number
  discount_amount: number
  extra_total: number
  subtotal: number
  service_name_snapshot: string
  service_option_name_snapshot: string
  service_abbreviation_snapshot: string
  total_claimed?: number        // optional since not needed in forms
  remaining_on_hand?: number    // optional since not needed in forms
  extras: JobItemExtra[]
}

export interface Payment {
  date_received: Date
  account_name: string
  amount: number
  reference_number: string
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
  job_items: JobItem[]
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
  job_items: JobItem[]
  payments?: Payment[]
  claims?: ClaimingHistory[]
}
