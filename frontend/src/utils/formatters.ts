export const formatCurrency = (value: number) =>
	new Intl.NumberFormat('en-PH', {
		style: 'currency',
		currency: 'PHP',
	}).format(value)

export const formatDate = (dateString: string) => {
	const date = new Date(dateString)
	return date.toLocaleDateString('en-US', {
		month: 'short', // e.g. Jul
		day: 'numeric', // e.g. 28
		year: 'numeric', // e.g. 2025
	})
}