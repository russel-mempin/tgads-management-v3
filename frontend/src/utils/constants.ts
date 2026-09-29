import type { SizeUnit, JobStatus } from '@/types/jobOrder'

export const MEASUREMENT_UNITS: SizeUnit[] = [
  'meter',
  'in.',
  'ft.',
  'cm.',
  'mm.',
]

export const JOB_STATUSES: JobStatus[] = [
  'Pending',
  'For Layout',
  'For Approval',
  'For Printing',
  'For Pickup',
  'Released',
]

export const PAYMENT_STATUSES = [
  { label: "Unpaid", value: "UNPAID" },
  { label: "Partial", value: "PARTIAL" },
  { label: "Fully Paid", value: "FULLY_PAID" },
  { label: "Credit", value: "CREDIT" },
  { label: "Refunded", value: "REFUNDED" },
  { label: "Overcharged", value: "OVERCHARGED" },
] as const

export const PRICE_UNITS = {
  PCS: 'pcs',
  SQIN: 'sqin',
  SQFT: 'sqft',
  SQM: 'sqm',
} as const

export type PriceUnit =
  typeof PRICE_UNITS[keyof typeof PRICE_UNITS]

export const PRICING_STRATEGIES = {
  AREA: 'Area',
  BY_PIECE: 'By Piece',
  FIXED: 'Fixed',
} as const

export type PricingStrategy =
  typeof PRICING_STRATEGIES[keyof typeof PRICING_STRATEGIES]

export type TRANSACTION_CATEGORIES =
  | "payment"
  | "expense"
  | "misc_sale"
  | "transfer"
  | "adjustment"
  | "reversal"
  | "refund"

export type DATE_PERIODS =
  | 'today'
  | 'this_week'
  | 'this_month'
  | 'last_month'
  | 'this_year'
  | 'all'