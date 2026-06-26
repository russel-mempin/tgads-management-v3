import type { JobItemFromDB } from '@/types/job_orders'

export const formatCurrency = (value: number | undefined) => {
  if (value === undefined) return '₱ 0.00'
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  })
    .format(value)
    .replace('₱', '₱ ')
}

export const nowInManila = () => {
    return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Manila' }))
}

export const formatDate = (date: string | Date | undefined) => {
  if (!date) return ''
  let parsedDate: Date
  if (typeof date === 'string') {
    // Append Z if no timezone info present, so JS treats it as UTC
    const normalized = date.endsWith('Z') || date.includes('+') ? date : date + 'Z'
    parsedDate = new Date(normalized)
  } else {
    parsedDate = date
  }
  return parsedDate.toLocaleString('en-PH', {
    timeZone: 'Asia/Manila',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

export const formatDateNoYear = (date: string | Date | undefined) => {
  if (!date) return ''
  let parsedDate: Date
  if (typeof date === 'string') {
    // Append Z if no timezone info present, so JS treats it as UTC
    const normalized = date.endsWith('Z') || date.includes('+') ? date : date + 'Z'
    parsedDate = new Date(normalized)
  } else {
    parsedDate = date
  }
  return parsedDate.toLocaleString('en-PH', {
    timeZone: 'Asia/Manila',
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
    case 'For Layout':
      return '!bg-yellow-500 !text-white'
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

export const getOverallJobStatus = (jobItems: JobItemFromDB[]): string => {
  if (!jobItems || jobItems.length === 0) return '—'

  return jobItems.reduce((prev, curr) => {
    const prevPriority = STATUS_PRIORITY[prev] ?? -1
    const currPriority = STATUS_PRIORITY[curr.job_status] ?? -1
    return currPriority > prevPriority ? curr.job_status : prev
  }, '' as string)
}

export const mapExpenseCategory = (category: string): string => {
  switch (category) {
    case 'Food':
      return '!bg-orange-500 !text-white'
    case 'Maintenance':
      return '!bg-gray-500 !text-white'
    case 'Utilities':
      return '!bg-yellow-500 !text-white'
    case 'Transportation':
      return '!bg-blue-500 !text-white'
    case 'Supplies':
      return '!bg-teal-500 !text-white'
    case 'Payroll':
      return '!bg-green-600 !text-white'
    case 'Benefits':
      return '!bg-purple-500 !text-white'
    case 'Production':
      return '!bg-red-500 !text-white'
    case 'Miscellaneous':
      return '!bg-slate-400 !text-white'
    default:
      return ''
  }
}
