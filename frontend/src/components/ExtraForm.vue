<script setup lang="ts">
import type { ExtraService } from '@/types/services';
import { ref, watch } from 'vue';
import { Button, Dialog, InputText, InputNumber, Select } from 'primevue';
import { X, Check } from '@lucide/vue';
import { useToast } from 'primevue';
import { createExtra } from '@/api/services';

const toast = useToast()

const props = defineProps<{
	isVisible: boolean
	editData?: ExtraService | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'saved'): void
}>()

const extra = ref<ExtraService>({
	name: '',
	price: 1,
});

const resetData = () => {
	extra.value = {
		name: '',
		price: 1,
	}
}

watch(() => props.editData, (newData) => {
	if (newData) {
		extra.value = { ...newData }
	} else {
		resetData()
	}
})

const onSave = async () => {
	try {
		if (props.editData) {
			// await editService(props.editData.id, extra.value)
		} else {
			await createExtra(extra.value)
		}
		toast.add({ severity: 'success', summary: 'Saved', detail: 'Service saved successfully.', life: 3000 })
		emit('saved')
		emit('update:isVisible', false)
		resetData()
	} catch (error: any) {
		toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save service.', life: 3000 })
		console.error(error.response?.data || error)
	}
}
</script>
<template>
	<Dialog :visible="isVisible" @update:visible="emit('update:isVisible', $event)" modal
		:header="editData ? 'Edit Extra' : 'Add Extra'" :style="{ width: '40rem' }">
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Name</label>
			<InputText v-model="extra.name" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Price</label>
			<InputNumber v-model="extra.price" mode="currency" currency="PHP" locale="en-PH" />
		</div>
		<div class="flex justify-end gap-2">
			<Button class="w-20" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button class="w-20" label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>