import type { JobItem } from '@/types/job_orders'

export const formatCurrency = (value: number | undefined) => {
  if (value === undefined) return '₱0.00'
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(value)
}

export const formatDate = (date: string | Date | undefined) => {
  if (!date) return ''
  const parsedDate = typeof date === 'string' ? new Date(date) : date
  return parsedDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

export const mapSeverity = (status: string) => {
  switch (status) {
    case 'For Approval':
      return 'info'
    case 'For Pickup':
      return 'info'
    case 'Released':
      return 'success'
    case 'Fully Paid':
      return 'success'
    case 'Cancelled':
      return 'danger'
    case 'Unpaid':
      return 'danger'
    case 'Credit':
      return 'danger'
    case 'Refunded':
      return 'danger'
    default:
      return 'contrast'
  }
}

export const mapCustomColor = (status: string): string | null => {
  switch (status) {
    case 'Overcharged':
      return '!bg-purple-500 !text-white'
    case 'Pending':
      return '!bg-orange-600 !text-white'
    default:
      return null
  }
}

export const formatNullable = (value: string | null | undefined) => {
  if (!value || value === 'null') return '-'
  return value
}

const STATUS_PRIORITY: Record<string, number> = {
  Cancelled: 0,
  Released: 1,
  'For Pickup': 2,
  'For Printing': 3,
  'For Approval': 4,
  'For Layout': 5,
  Pending: 6,
}

export const getOverallJobStatus = (jobItems: JobItem[]): string => {
  if (!jobItems || jobItems.length === 0) return '—'

  return jobItems.reduce((prev, curr) => {
    const prevPriority = STATUS_PRIORITY[prev] ?? -1
    const currPriority = STATUS_PRIORITY[curr.job_status] ?? -1
    return currPriority > prevPriority ? curr.job_status : prev
  }, '' as string)
}
