<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { ExpenseList, ExpensePeriod } from '@/types/expense';
import { getAllExpenses, getExpenseCount } from '@/api/expenses';
import MiscSaleForm from '@/components/MiscSaleForm.vue';
import ExpenseTable from '@/components/ExpenseTable.vue';
import ExpenseCards from '@/components/ExpenseCards.vue';

const descriptionSearch = ref('')
const period = ref<ExpensePeriod>('this_month')
const includeArchived = ref(false)
const data = ref<ExpenseList[]>([])

const loading = ref(false)
const isAddMiscSaleFormOpen = ref(false)

// Pagination
const currentPage = ref(1)
const rows = ref(20)
const totalRecords = ref(0)
const currentOffset = computed(() => (currentPage.value - 1) * rows.value)

const fetchData = async () => {
	loading.value = true

	try {
		data.value = await getAllExpenses(
			period.value,
			includeArchived.value,
			currentOffset.value,
			rows.value
		)

		totalRecords.value = data.value.
	}
	finally {
		loading.value = false
	}
}

onMounted(async () => {
	await fetchData()
})

watch([currentPage, rows], fetchData)

watch(includeArchived, async () => {
	await fetchData()
})
</script>

<template>
	<MiscSaleForm v-model:is-open="isAddMiscSaleFormOpen" />
	<div class="h-full min-h-0 flex flex-col">
		<section class="shrink-0 mx-6 mt-6 flex justify-between">
			<div class="flex gap-2">
				<UButton label="Today" class="rounded-full" />
				<UButton label="This Week" class="rounded-full" />
				<UButton label="This Month" class="rounded-full" />
				<UButton label="Last Month" class="rounded-full" />
				<UButton label="This Year" class="rounded-full" />
				<UButton label="All Time" class="rounded-full" />
			</div>
			<UButton label="Add Expense" icon="i-lucide-plus" color="primary" size="lg"
				@click="() => isAddMiscSaleFormOpen = true" />
		</section>
		<section class="shrink-0 mx-6 mt-6 grid grid-cols-3 gap-6">
			<ExpenseCards />
		</section>
		<section class="shrink-0 flex-1 flex flex-col min-h-0 mx-6 mt-6 border border-default bg-default rounded-md">
			<UInput size="lg" class="p-4" v-model="descriptionSearch" placeholder="Search by description" />
			<ExpenseTable sticky class="overflow-y-auto h-full" :expense="data">
				<template #actions="{ item }">
					<UButton icon="i-lucide-square-pen" variant="ghost" size="md" />
					<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" />
				</template>
			</ExpenseTable>
		</section>
		<section class="shrink-0 flex-1 min-h-0 mx-6 my-6 border border-default bg-default rounded-md p-4">
			<p class="text-lg">Expense By Category</p>
			<div>
				
			</div>
		</section>
	</div>
</template>