export const formatCurrency = (value: number | undefined) => {
  if (value === undefined) return '₱ 0.00'
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  })
    .format(value)
    .replace('₱', '₱ ')
}

export function nowForInput(): string {
  const date = new Date()
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}

export function utcToInput(value: string): string {
  const date = new Date(value)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}

export function inputToUtc(value: string): string {
  return new Date(value).toISOString()
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

export const formatNullable = (value: string | null | undefined) => {
  if (!value || value === 'null') return '-'
  return value
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

type BadgeColor = 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'primary'

const paymentStatusColors: Record<string, BadgeColor> = {
    'Fully Paid': 'success',
    'Partial': 'warning',
    'Unpaid': 'error',
    'Credit': 'info',
    'Refunded': 'neutral',
    'Overcharged': 'warning',
}

const jobStatusColors: Record<string, BadgeColor> = {
    'Pending': 'warning',
    'For Layout': 'info',
    'For Approval': 'primary',
    'For Printing': 'primary',
    'For Pickup': 'success',
    'Released': 'neutral',
    'Cancelled': 'error',
}

export const getPaymentStatusColor = (status?: string): BadgeColor =>
    paymentStatusColors[status ?? 'Unpaid'] ?? 'error'

export const getJobStatusColor = (status?: string): BadgeColor =>
    jobStatusColors[status ?? 'Pending'] ?? 'warning'