<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { Expense } from '@/types/expense';
import { getAllExpenses } from '@/api/expenses';
import MiscSaleForm from '@/components/MiscSaleForm.vue';
import ExpenseTable from '@/components/ExpenseTable.vue';

const descriptionSearch = ref('')
const includeArchived = ref(false)
const data = ref<Expense[]>([])

const loading = ref(false)
const isAddMiscSaleFormOpen = ref(false)

const fetchData = async () => {
	loading.value = true
	try {
		data.value = await getAllExpenses(includeArchived.value)
		console.log(data.value)
	}
	finally {
		loading.value = false
	}
}

onMounted(async () => {
	await fetchData()
})

watch(includeArchived, async () => {
	await fetchData()
})
</script>

<template>
	<MiscSaleForm v-model:is-open="isAddMiscSaleFormOpen" />
	<div class="h-full min-h-0 flex flex-col">
		<section class="shrink-0 mx-6 mt-6 flex gap-6 items-center">
			<UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
			<USwitch label="Include archived" v-model="includeArchived" />
			<UButton label="Add Expense" icon="i-lucide-plus" color="primary" size="lg" @click="() => isAddMiscSaleFormOpen = true" />
		</section>
		<section class="shrink-0 flex-1 min-h-0 mx-6 mt-6 border border-default bg-default rounded-md">
			<ExpenseTable :expense="data">
				<template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" />
                    <UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" />
                </template>
			</ExpenseTable>
		</section>
	</div>
</template>