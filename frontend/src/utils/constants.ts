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