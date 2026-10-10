<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { ExpenseList, ExpensePeriod, ExpenseCategory, ExpenseCreate } from '@/types/expense';
import { getAllExpenses, createExpense } from '@/api/expenses';
import ExpenseForm from '@/components/ExpenseForm.vue';
import ExpenseTable from '@/components/ExpenseTable.vue';
import ExpenseCards from '@/components/ExpenseCards.vue';
import { useAuthStore } from '@/stores/auth';
import SpendingByCategory from '@/components/SpendingByCategory.vue';
import axios from 'axios';

const authStore = useAuthStore()
const toast = useToast()

const data = ref<ExpenseList>({
	items: [],
	total_items: 0,
	summary: {
		total: '0',
		count: 0,
		largest: null,
	},
	expense_by_category: []
})

const loading = ref(false)
const isExpenseFormOpen = ref(false)

// Filtering
const period = ref<ExpensePeriod>('this_month')
const descriptionSearch = ref('')
const category = ref<ExpenseCategory | 'all'>('all')
const includeArchived = ref(false)

// UI Variables
const periods: { label: string; value: ExpensePeriod }[] = [
	{ label: 'Today', value: 'today' },
	{ label: 'This Week', value: 'this_week' },
	{ label: 'This Month', value: 'this_month' },
	{ label: 'Last Month', value: 'last_month' },
	{ label: 'This Year', value: 'this_year' },
	{ label: 'All Time', value: 'all' },
]
const categories = [
	{ label: 'All Categories', value: 'all' },
	{ label: 'Food', value: 'Food' },
	{ label: 'Maintenance', value: 'Maintenance' },
	{ label: 'Utilities', value: 'Utilities' },
	{ label: 'Transportation', value: 'Transportation' },
	{ label: 'Supplies', value: 'Supplies' },
	{ label: 'Payroll', value: 'Payroll' },
	{ label: 'Benefits', value: 'Benefits' },
	{ label: 'Production', value: 'Production' },
	{ label: 'Miscellaneous', value: 'Miscellaneous' },
	{ label: 'Equipment', value: 'Equipment' },
]

// Pagination
const currentPage = ref(1)
const rows = ref(10)
const totalRecords = ref(0)
const currentOffset = computed(() => (currentPage.value - 1) * rows.value)

// Data Functions
const fetchData = async () => {
	loading.value = true
	try {
		data.value = await getAllExpenses(
			period.value,
			includeArchived.value,
			category.value === 'all' ? undefined : category.value,
			descriptionSearch.value,
			currentOffset.value,
			rows.value
		)
		totalRecords.value = data.value.total_items
	}
	finally {
		loading.value = false
	}
}

onMounted(fetchData)

watch(
	[period, includeArchived, category, descriptionSearch],
	() => {
		currentPage.value = 1
		fetchData()
	}
)

watch(
	[currentPage, rows],
	fetchData
)

const saveNewExpenseToDb = async (expense: ExpenseCreate) => {
	loading.value = true
	try {
		await createExpense(expense)
		toast.add({
			title: 'Expense Added.',
			color: 'success',
			icon: 'i-lucide-circle-check'
		})
		await fetchData()
		isExpenseFormOpen.value = false
	}
	catch (error: unknown) {
		console.error('Failed to create expense:', error)

		let message = 'An unexpected error occurred.'

		if (axios.isAxiosError(error)) {
			message = error.response?.data?.detail ?? 'Failed to create expense.'
		}

		toast.add({
			title: 'Saving data failed.',
			description: message,
			color: 'error',
			icon: 'i-lucide-x'
		})
	}
	finally {
		loading.value = false
	}
}
</script>

<template>
	<ExpenseForm v-model:is-open="isExpenseFormOpen" @save="saveNewExpenseToDb" />
	<div class="flex h-full min-h-0 flex-col" :class="authStore.isOwner && 'overflow-y-auto'">
		<section class="shrink-0 mx-6 mt-6 flex justify-between">
			<div class="flex gap-2">
				<UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
					:variant="period === item.value ? 'solid' : 'outline'" @click="() => { period = item.value }" />
			</div>
			<UButton label="Add Expense" icon="i-lucide-plus" color="primary" size="lg"
				@click="() => { isExpenseFormOpen = true }" />
		</section>
		<section v-if="authStore.isOwner" class="shrink-0 mx-6 mt-6 grid grid-cols-3 gap-6">
			<ExpenseCards :summary="data.summary" :period="period" />
		</section>
		<section class="mx-6 mt-6 flex flex-col overflow-hidden border border-default bg-default rounded-md"
			:class="authStore.isOwner ? 'shrink-0 h-[36rem]' : 'min-h-0 flex-1 mb-6'">
			<div class="flex items-center gap-4 p-4">
				<UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
				<USwitch v-if="authStore.isOwner" label="Include archived" v-model="includeArchived" />
				<USelect size="lg" class="w-48" v-model="category" :items="categories" />
			</div>
			<ExpenseTable sticky class="min-h-0 flex-1 overflow-y-auto" :expense="data.items">
				<template #actions="{ item }">
					<UButton icon="i-lucide-square-pen" variant="ghost" size="md" />
					<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" />
				</template>
			</ExpenseTable>
			<div class="border-t border-default flex items-center justify-between p-4">
				<p class="text-muted text-sm">
					Showing
					{{ data.items.length ? currentOffset + 1 : 0 }}–{{
						Math.min(currentOffset + data.items.length, totalRecords)
					}}
					of {{ totalRecords }}
				</p>
				<UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
			</div>
		</section>
		<section v-if="authStore.isOwner" class="mx-6 my-6 border border-default bg-default rounded-md p-4">
			<SpendingByCategory :data="data.expense_by_category" />
		</section>
	</div>
</template>