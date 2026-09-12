<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { MiscSale, MiscSaleCreate, MiscSaleUpdate } from '@/types/miscSale';
import { createMiscSale, getAllMiscSales, updateMiscSale, archiveMiscSale } from '@/api/miscSales';
import MiscSaleTable from '@/components/MiscSaleTable.vue';
import MiscSaleForm from '@/components/MiscSaleForm.vue';
import axios from 'axios';
import { useReferenceStore } from '@/stores/reference';
import { useAuthStore } from '@/stores/auth';
import ConfirmDeleteMiscSale from '@/components/ConfirmDeleteMiscSale.vue';
import { formatDate } from '@/utils/formatters';

const authStore = useAuthStore()
const toast = useToast()
const referenceStore = useReferenceStore()

const descriptionSearch = ref('')
const includeArchived = ref(false)
const data = ref<MiscSale[]>([])
const selectedMiscSale = ref<MiscSale>()
const originalMiscSale = ref<MiscSale>()

const loading = ref(false)
const isAddMiscSaleFormOpen = ref(false)
const isConfirmDeleteModalOpen = ref(false)

const fetchData = async () => {
	loading.value = true
	try {
		data.value = await getAllMiscSales(includeArchived.value)
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

const saveNewMiscSaleToDb = async (item: MiscSaleCreate) => {
	try {
		if (!selectedMiscSale.value) {
			await createMiscSale(item as MiscSaleCreate)
			toast.add({
				title: 'Misc Sale Added.',
				color: 'success',
				icon: 'i-lucide-circle-check'
			})
		}
		else {
			const changes: MiscSaleUpdate = {}

			for (const key of Object.keys(item) as (keyof MiscSaleUpdate)[]) {
				const currentValue = item[key]
				const originalValue = originalMiscSale.value?.[key]

				const changed =
					key === 'date'
						? new Date(currentValue as string).getTime() !==
						new Date(originalValue as string).getTime()
						: currentValue !== originalValue

				if (changed) {
					changes[key] = currentValue as never
				}
			}
			await updateMiscSale(selectedMiscSale.value.id, changes)
			toast.add({
				title: 'Misc Sale Updated.',
				color: 'success',
				icon: 'i-lucide-circle-check'
			})
		}
		await fetchData()
		selectedMiscSale.value = undefined
	}
	catch (error: unknown) {
		console.error('Failed to create misc sale:', error)

		let message = 'An unexpected error occurred.'

		if (axios.isAxiosError(error)) {
			message = error.response?.data?.detail ?? 'Failed to create misc sale.'
		}

		toast.add({
			title: 'Saving data failed.',
			description: message,
			color: 'error',
			icon: 'i-lucide-x'
		})
	}
}
const openAddMiscSaleForm = () => {
	isAddMiscSaleFormOpen.value = true
	selectedMiscSale.value = undefined
}
const openEditMiscSaleForm = (item: MiscSale) => {
	const account = referenceStore.accountOptions.find(
		acc => acc.name === item.account_name
	)
	if (!account) {
		console.error(`No matching account: ${item.account_name}`)
		return
	}
	const sale = {
		...item,
		account_id: account.id,
		amount: item.amount
	}
	selectedMiscSale.value = { ...sale }
	originalMiscSale.value = { ...sale }

	isAddMiscSaleFormOpen.value = true
}
const openDeleteMiscSaleModal = (item: MiscSale) => {
	selectedMiscSale.value = item
	isConfirmDeleteModalOpen.value = true
}
const deleteMiscSale = async () => {
	if (!selectedMiscSale.value) return
	try {
		await archiveMiscSale(selectedMiscSale.value.id)
		toast.add({
			title: 'Misc Sale archived.',
			color: 'success',
			icon: 'i-lucide-circle-check'
		})
	}
	catch(error: unknown) {
		console.error('Failed to archive misc sale:', error)

		let message = 'An unexpected error occurred.'

		if (axios.isAxiosError(error)) {
			message = error.response?.data?.detail ?? 'Failed to archive misc sale.'
		}

		toast.add({
			title: 'Archiving failed.',
			description: message,
			color: 'error',
			icon: 'i-lucide-x'
		})
	}
}
</script>

<template>
	<ConfirmDeleteMiscSale v-model:open="isConfirmDeleteModalOpen" title="You are about to delete a misc. sale"
		description="This will delete the misc. sale data and reverse the transaction related to it."
		@confirm="deleteMiscSale">
		<template #details>
			<div class="flex justify-between gap-4">
				<span class="text-sm text-muted">Description</span>
				<span class="text-sm font-medium text-highlighted">
					{{ selectedMiscSale?.description }}
				</span>
			</div>

			<div class="mt-2 flex justify-between gap-4">
				<span class="text-sm text-muted">Amount</span>
				<span class="text-sm font-medium text-highlighted">
					₱{{ selectedMiscSale?.amount }}
				</span>
			</div>

			<div class="mt-2 flex justify-between gap-4">
				<span class="text-sm text-muted">Date</span>
				<span class="text-sm font-medium text-highlighted">
					{{ formatDate(selectedMiscSale?.date) }}
				</span>
			</div>
		</template>
	</ConfirmDeleteMiscSale>
	<MiscSaleForm v-model:is-open="isAddMiscSaleFormOpen" @save="saveNewMiscSaleToDb"
		:editing-misc-sale="selectedMiscSale" />
	<div class="m-6">
		<section class="flex gap-6 items-center">
			<UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
			<USwitch v-if="authStore.isOwner" label="Include archived" v-model="includeArchived" />
			<UButton label="Add Misc Sale" icon="i-lucide-plus" color="primary" size="lg"
				@click="openAddMiscSaleForm" />
		</section>
		<section class="mt-6 border border-default bg-default rounded-md">
			<MiscSaleTable :misc-sale="data">
				<template #actions="{ item }">
					<UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditMiscSaleForm(item)" />
					<UButton icon="i-lucide-trash-2" variant="ghost" color="error" size="md"
						@click="openDeleteMiscSaleModal(item)" />
				</template>
			</MiscSaleTable>
		</section>
	</div>
</template>