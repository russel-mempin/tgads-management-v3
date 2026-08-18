import type { SizeUnit, JobStatus } from '@/types/jobOrder'

export const MEASUREMENT_UNITS: { label: string; value: SizeUnit }[] = [
    { label: 'meter', value: 'METER' },
    { label: 'in.', value: 'INCHES' },
    { label: 'ft.', value: 'FEET' },
    { label: 'cm.', value: 'CENTIMETER' },
    { label: 'mm.', value: 'MILLIMETER' },
]

export const JOB_STATUSES: { label: string; value: JobStatus }[] = [
  { label: "Pending", value: "PENDING" },
  { label: "For Layout", value: "FOR_LAYOUT" },
  { label: "For Approval", value: "FOR_APPROVAL" },
  { label: "For Printing", value: "FOR_PRINTING" },
  { label: "For Pickup", value: "FOR_PICKUP" },
  { label: "Released", value: "RELEASED" },
]

export const PAYMENT_STATUSES = [
  { label: "Unpaid", value: "UNPAID" },
  { label: "Partial", value: "PARTIAL" },
  { label: "Fully Paid", value: "FULLY_PAID" },
  { label: "Credit", value: "CREDIT" },
  { label: "Refunded", value: "REFUNDED" },
  { label: "Overcharged", value: "OVERCHARGED" },
] as const