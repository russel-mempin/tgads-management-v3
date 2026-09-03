<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { MiscSale } from '@/types/miscSale';
import { getAllMiscSales } from '@/api/miscSales';
import MiscSaleTable from '@/components/MiscSaleTable.vue';
import MiscSaleForm from '@/components/MiscSaleForm.vue';

const descriptionSearch = ref('')
const includeArchived = ref(false)
const data = ref<MiscSale[]>([])

const loading = ref(false)
const isAddMiscSaleFormOpen = ref(false)

const fetchData = async () => {
	loading.value = true
	try {
		data.value = await getAllMiscSales(includeArchived.value)
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
	<div class="m-6">
		<section class="flex gap-6 items-center">
			<UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
			<USwitch label="Include archived" v-model="includeArchived" />
			<UButton label="Add Expense" icon="i-lucide-plus" color="primary" size="lg" @click="() => isAddMiscSaleFormOpen = true" />
		</section>
		<section class="mt-6 border border-default bg-default rounded-md">
			<MiscSaleTable :misc-sale="data">
				<template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" />
                    <UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md" />
                </template>
			</MiscSaleTable>
		</section>
	</div>
</template>