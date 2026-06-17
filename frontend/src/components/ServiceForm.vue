<script setup lang="ts">
import type { ServiceCreate, ServiceType } from '@/types/services';
import { ref, watch } from 'vue';
import { Button, Dialog, InputText, InputNumber, Select } from 'primevue';
import { X, Check } from '@lucide/vue';
import { useToast } from 'primevue';
import { createService, editService } from '@/api/services';

const toast = useToast()

const props = defineProps<{
	isVisible: boolean
	editData?: ServiceType | null
}>()

const emit = defineEmits<{
	(e: 'update:isVisible', value: boolean): void
	(e: 'saved'): void
}>()

const service = ref<ServiceCreate>({
	name: '',
	abbreviation: '',
	price: 1,
	unit: 'sqft',
	is_area_based: true,
});

const units = ref(['sqft', 'sqin', 'sqm']);
const onAbbreviationInput = (e: Event) => {
	const input = e.target as HTMLInputElement
	service.value.abbreviation = input.value.toUpperCase().replace(/\s/g, '')
}

const resetData = () => {
	service.value = {
		name: '',
		abbreviation: '',
		price: 1,
		unit: 'sqft',
		is_area_based: true,
	}
}

watch(() => props.editData, (newData) => {
	if (newData) {
		service.value = { ...newData }
	} else {
		resetData()
	}
})

const onSave = async () => {
	try {
		if (props.editData) {
			await editService(props.editData.id, service.value)
		} else {
			await createService(service.value)
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
		:header="editData ? 'Edit Service' : 'Add Service'" :style="{ width: '40rem' }">
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Name</label>
			<InputText v-model="service.name" />
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Abbreviation</label>
			<InputText v-model="service.abbreviation" @input="onAbbreviationInput" />
		</div>
		<div class="grid grid-cols-2 gap-4">
			<div class="flex flex-col mb-4">
				<label class="font-semibold mb-1">Price</label>
				<InputNumber v-model="service.price" mode="currency" currency="PHP" locale="en-PH" />
			</div>
			<div class="flex flex-col mb-4">
				<label class="font-semibold mb-1">Unit</label>
				<Select v-model="service.unit" :options="units" />
			</div>
		</div>
		<div class="flex flex-col mb-4">
			<label class="font-semibold mb-1">Is Area Based</label>
			<div class="pill-toggle" :class="service.is_area_based ? 'on' : 'off'"
				@click="service.is_area_based = !service.is_area_based">
				<div class="pill-icon" :class="{ active: !service.is_area_based }">
					<X :size="16" />
				</div>
				<div class="pill-icon" :class="{ active: service.is_area_based }">
					<Check :size="16" />
				</div>
			</div>
		</div>
		<div class="flex justify-end gap-2">
			<Button class="w-20" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
			<Button class="w-20" label="Save" @click="onSave" />
		</div>
	</Dialog>
</template>

<style scoped>
.pill-toggle {
	display: flex;
	align-items: center;
	border: 2px solid;
	border-radius: 10px;
	padding: 4px;
	cursor: pointer;
	width: 100%;
	transition: border-color 0.2s;
}

.pill-icon {
	flex: 1;
	height: 32px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--color-text-secondary);
	transition: background 0.2s, color 0.2s;
}

.pill-toggle.on {
	border-color: #22c55e;
}

.pill-toggle.off {
	border-color: #ef4444;
}

.pill-toggle.on .pill-icon.active {
	background: #22c55e;
	color: white;
}

.pill-toggle.off .pill-icon.active {
	background: #ef4444;
	color: white;
}
</style>