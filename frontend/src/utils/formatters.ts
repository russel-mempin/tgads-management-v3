export const formatCurrency = (value: number) =>
  new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(value)

export const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

export const mapSeverity = (status: string) => {
  switch (status) {
    case 'For Layout':
      return 'warn'
    case 'Partial':
      return 'warn'
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
