<script setup lang="ts">
import { reactive, watch } from 'vue'
import { z } from 'zod'
import type { ServiceOption } from '@/types/service';
import { nowForInput, inputToUtc, utcToInput } from '@/utils/formatters';

const props = defineProps<{
    parent_service_id: string,
	editingOption?: ServiceOption | null
}>()

const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const schema = z.object({
	claimed_item_id: z.string().min(1, 'Identify what item was claimed'),
	pcs_claimed: z.number({ error: 'Pieces Claimed is required' }).positive('Value must be greater than 0'),
	date_claimed: z.string().min(1, 'Date claimed is required'),
	name: z.string().min(1, 'Name is required'),
})
type Schema = z.output<typeof schema>
const getInitialState = (): Schema => ({
	claimed_item_id: '',
	pcs_claimed: 1,
	date_claimed: nowForInput(),
	name: '',
})
const state = reactive<Schema>(getInitialState())
</script>

<template>
    <UModal :title="editingOption ? 'Edit Option' : 'Add Option'" v-model:open="isOpen"
        :close="{ color: 'error', class: 'rounded-full' }"
        description="Enter payment data and click save to prepare it for saving.">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-6" @submit="onSubmit">
                <div class="grid grid-cols-2 gap-6">
                    <UFormField label="Claimed Item" name="claimed_item_id" required class="w-full">
                        <USelect v-model="state.claimed_item_id" :items="claimableItemIds"
                            placeholder="Select item to claim" class="w-full" value-key="value" />
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
                    <UInput v-model="state.name" class="w-full" placeholder="e.g. Juan Dela Cruz" />
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