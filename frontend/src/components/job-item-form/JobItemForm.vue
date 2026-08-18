<script setup lang="ts">
import type { JobItemCreate } from '@/types/jobOrder';

const props = defineProps<{
	editingItem?: JobItemCreate | null
	currentItemIds?: string[]
	joNumber?: number
}>()

const emit = defineEmits<{
	save: [item: JobItemCreate]
}>()

const isOpen = defineModel<boolean>('isOpen', { required: true })
</script>

<template>
	<JobItemFormModal v-model:is-open="isOpen" :editing-item="editingItem" :current-item-ids="currentItemIds"
		:jo-number="joNumber" @save="emit('save', $event)" />
</template>