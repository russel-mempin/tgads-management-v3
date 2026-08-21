<script setup lang="ts">
import { formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	totalDue: number
	totalPaid: number
	balance: number
	canSave: boolean
}>()

const emit = defineEmits<{
	save: []
}>()
</script>

<template>
	<div
		class="sticky grid grid-cols-2 gap-8 bottom-0 px-8 py-4 w-full shrink-0 border-t border-default backdrop-blur bg-default/60">
		<div class="flex gap-8 items-center">
			<div>
				<p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Due</p>
				<p class="text-lg font-bold text-highlighted">{{ formatCurrency(totalDue) }}</p>
			</div>
			<div>
				<p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Paid</p>
				<p class="text-lg font-bold text-highlighted">{{ formatCurrency(totalPaid) }}</p>
			</div>
			<div>
				<p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Balance</p>
				<p class="text-lg font-bold text-highlighted">{{ formatCurrency(balance) }}</p>
			</div>
		</div>
		<div class="flex gap-8 items-center justify-end">
			<UButton icon="i-lucide-arrow-left" color="neutral" class="w-45 font-bold" variant="outline">Back to Job
				Orders
			</UButton>
			<UButton class="w-45 font-bold relative" @click="emit('save')" :disabled="canSave" loading-auto>
				<template #leading>
					<UIcon name="i-lucide-save" class="absolute left-3 size-5" />
				</template>
				<span class="w-full text-center">Save</span>
			</UButton>
		</div>
	</div>
</template>