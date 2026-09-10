<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { ExpenseList, ExpensePeriod, ExpenseCategory } from '@/types/expense';
import { getAllExpenses } from '@/api/expenses';
import MiscSaleForm from '@/components/MiscSaleForm.vue';
import ExpenseTable from '@/components/ExpenseTable.vue';
import ExpenseCards from '@/components/ExpenseCards.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()

const data = ref<ExpenseList>({
	items: [],
	total_items: 0,
	summary: {
		total: '0',
		count: 0,
		largest: null,
	},
})

const loading = ref(false)
const isAddMiscSaleFormOpen = ref(false)

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
</script>

<template>
	<MiscSaleForm v-model:is-open="isAddMiscSaleFormOpen" />
	<div class="flex flex-col">
		<section class="shrink-0 mx-6 mt-6 flex justify-between">
			<div class="flex gap-2">
				<UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
					:variant="period === item.value ? 'solid' : 'outline'" @click="period = item.value" />
			</div>
			<UButton label="Add Expense" icon="i-lucide-plus" color="primary" size="lg"
				@click="() => isAddMiscSaleFormOpen = true" />
		</section>
		<section class="shrink-0 mx-6 mt-6 grid grid-cols-3 gap-6">
			<ExpenseCards :summary="data.summary" :period="period" />
		</section>
		<section class="max-h-150 flex flex-col mx-6 mt-6 border border-default bg-default rounded-md">
			<div class="flex items-center gap-4 p-4">
				<UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
				<USwitch v-if="authStore.isOwner" label="Include archived" v-model="includeArchived" />
				<USelect size="lg" class="w-48" v-model="category" :items="categories" />
			</div>
			<ExpenseTable sticky class="overflow-y-auto h-full" :expense="data.items">
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
		<section class="mx-6 my-6 border border-default bg-default rounded-md p-4">
			<p class="text-lg">Expense By Category</p>
			<div>
			</div>
		</section>
	</div>
</template>