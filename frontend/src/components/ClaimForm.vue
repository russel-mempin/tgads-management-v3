<script setup lang="ts">
import { reactive, watch } from 'vue'
import { z } from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import type { JobItemCreate, ClaimingHistory } from '@/types/jobOrder';
import { nowForInput, inputToUtc } from '@/utils/formatters';

const props = defineProps<{
	jobItems: JobItemCreate[]
	editingClaim?: ClaimingHistory | null
}>()

const emit = defineEmits<{
	save: [claim: ClaimingHistory]
}>()

// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const schema = z.object({
	claimed_item_id: z.string().min(1, 'Identify what item was claimed'),
	pcs_claimed: z.number({ error: 'Pieces Claimed is required' }).positive('Value must be greater than 0'),
	date_claimed: z.string().min(1, 'Date claimed is required'),
	name: z.string().min(1, 'Name is required'),
})
type Schema = z.output<typeof schema>

// Input Variables
const getInitialState = (): Schema => ({
	claimed_item_id: '',
	pcs_claimed: 1,
	date_claimed: nowForInput(),
	name: '',
})
const state = reactive<Schema>(getInitialState())

// UI Functions
const resetForm = () => {
	Object.assign(state, getInitialState())
}
const handleCancel = () => {
	resetForm()
	isOpen.value = false
}

// Data Functions
watch([() => props.editingClaim, isOpen], ([claim, open]) => {
    if (open && claim) {
        Object.assign(state, {
            claimed_item_id: claim.claimed_item_id,
            pcs_claimed: claim.pcs_claimed,
            date_claimed: claim.date_claimed instanceof Date
                ? claim.date_claimed.toISOString().slice(0, 16)
                : String(claim.date_claimed).slice(0, 16),
            name: claim.name,
        })
    } else if (!open) {
        resetForm()
    }
})

const onSubmit = (event: FormSubmitEvent<Schema>) => {
	const payload: ClaimingHistory = {
		claimed_item_id: event.data.claimed_item_id,
		pcs_claimed: event.data.pcs_claimed,
		date_claimed: new Date(inputToUtc(event.data.date_claimed)),
		name: event.data.name
	}

	emit('save', payload)
	resetForm()
	isOpen.value = false
}
</script>

<template>
	<UModal :title="editingClaim ? 'Edit Claim' : 'Add Claim'" v-model:open="isOpen"
		:close="{ color: 'error', class: 'rounded-full' }"
		description="Enter payment data and click save to prepare it for saving.">
		<template #body>
			<UForm :schema="schema" :state="state" class="flex flex-col gap-6" @submit="onSubmit">
				<div class="grid grid-cols-2 gap-6">
					<UFormField label="Claimed Item" name="claimed_item_id" required class="w-full">
						<USelect v-model="state.claimed_item_id" :items="props.jobItems.map(item => ({
							label: `${item.item_id} — ${item.service_name_snapshot}`,
							value: item.item_id
						}))" placeholder="Select item to claim" class="w-full" value-key="value" />
					</UFormField>
					<UFormField label="Pieces Claimed" name="pcs_claimed" required class="w-full">
						<UInputNumber v-model="state.pcs_claimed" class="w-full" :increment="false" :decrement="false"
							@focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
					</UFormField>
				</div>
				<UFormField label="Date Claimed" name="date_claimed" required class="w-full">
					<UInput v-model="state.date_claimed" type="datetime-local" class="w-full" />
				</UFormField>
				<UFormField label="Name" name="name" required class="w-full">
					<UInput v-model="state.name" class="w-full" placeholder="e.g. Juan Dela Cruz"/>
				</UFormField>
				<div class="flex justify-end gap-4">
					<UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg" class="w-28"
						@click="handleCancel" />
					<UButton label="Save" icon="i-lucide-save" color="primary" size="lg" class="w-28 font-semibold"
						type="submit" />
				</div>
			</UForm>
		</template>
	</UModal>
</template>