export type SizeUnit = 'meter' | 'in.' | 'ft.' | 'cm.' | 'mm.'
export type JobStatus =
  | 'Pending'
  | 'For Layout'
  | 'For Approval'
  | 'For Printing'
  | 'For Pickup'
  | 'Released'
  | 'Cancelled'
export type PaymentStatus = 'Fully Paid' | 'Partial' | 'Unpaid' | 'Credit' | 'Refunded' | 'Overcharged'

export interface PricingData {
  consumption: number
  consumption_unit: string
  rate: number
  unit_price: number
}

export interface Dimensions {
  height?: number
  width?: number
  size_unit?: SizeUnit
}

export interface JobItemExtra {
  id?: string
  extra_service_id: string
  quantity: number
  price_snapshot: number
  name_snapshot: string
}

export type JobItemExtraCreate = Pick<JobItemExtra, 'extra_service_id' | 'quantity'>

interface JobItemBase extends Dimensions {
  item_id: string
  description: string
  quantity: number
  job_status: JobStatus
  due_date: Date
  notes: string
  extra_charge: number
  discount_amount: number
  extras: JobItemExtra[]
}

interface ServiceRef {
  service_id: string
  service_option_id: string
}

interface ServiceSnapshot {
  service_name_snapshot: string
  service_option_name_snapshot: string
  service_abbreviation_snapshot?: string
}

interface JobItemComputed {
  unit_price: number
  subtotal: number
  total_claimed: number
  remaining_on_hand: number
}

export interface JobItemCreate extends Omit<JobItemBase, 'extras'>, ServiceRef {
  extras: JobItemExtraCreate[]
}

export type JobItemUpdate = Partial<Pick<JobItemBase, 'quantity' | 'job_status' | 'notes' | 'extra_charge' | 'discount_amount' | 'extras'>>

export interface JobItemTableRow extends JobItemBase, ServiceSnapshot, JobItemComputed {
  id?: string
}

export interface JobItem extends JobItemBase, ServiceRef, ServiceSnapshot, JobItemComputed {
  id: string
  service_abbreviation_snapshot: string
}

export interface Payment {
  date_received: Date
  reference_number: string
  amount: number
  notes: string
  account_id?: string
  account_name_snapshot: string
}

export interface ClaimingHistory {
  date_claimed: Date
  name: string
  pcs_claimed: number
  claimed_item_id: string
}

interface JobOrderBase {
  jo_number: number
  date_received: Date
  overall_job_status: JobStatus
  payment_status: PaymentStatus
}

export interface JobOrder extends JobOrderBase {
  id: string
  job_items: JobItem[]
  payments: Payment[]
  claiming_history: ClaimingHistory[]
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

export interface JobOrderCreate extends JobOrderBase {
  customer_id?: string
  customer_name?: string
  customer_address?: string
  customer_contact_no?: string
  customer_email?: string
  job_items: JobItemCreate[]
  payments?: Payment[]
  claims?: ClaimingHistory[]
}
