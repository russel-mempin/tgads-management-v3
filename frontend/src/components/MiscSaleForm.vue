<script setup lang="ts">
import { reactive, watch } from 'vue'
import { z } from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import type { MiscSaleCreate, MiscSale } from '@/types/miscSale'
import { inputToUtc, nowForInput, utcToInput } from '@/utils/formatters'
import { useReferenceStore } from '@/stores/reference'

const props = defineProps<{
    editingMiscSale?: MiscSale | null
}>()
const isOpen = defineModel<boolean>('isOpen', { required: true })
const emit = defineEmits<{
    save: [miscSale: MiscSaleCreate]
    close: []
}>()
const referenceStore = useReferenceStore()

// Validation Schema
const schema = z.object({
    date: z.string().min(1, 'Date is required'),
    referenceNumber: z.string().optional(),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    accountId: z.string().min(1, 'Payment method is required'),
    description: z.string().min(1, 'Description is required.'),
})
type Schema = z.output<typeof schema>

// Input Variables
const getInitialState = (): Schema => ({
    date: nowForInput(),
    referenceNumber: '',
    amount: 0,
    accountId: '',
    description: '',
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
watch(() => props.editingMiscSale, (miscSale) => {
    if (miscSale) {
        state.date = utcToInput(miscSale.date)
        state.referenceNumber = miscSale.reference_number ?? ''
        state.amount = Number(miscSale.amount)
        state.accountId = miscSale.account_id
        state.description = miscSale.description
    }
    else {
        resetForm()
    }
}, { immediate: true })

const onSubmit = (event: FormSubmitEvent<Schema>) => {
	const payload: MiscSaleCreate = {
        date: inputToUtc(event.data.date),
        description: event.data.description,
        reference_number: event.data.referenceNumber,
        amount: event.data.amount,
        account_id: event.data.accountId
	}
	emit('save', payload)
	resetForm()
	isOpen.value = false
}
</script>

<template>
    <UModal :title="props.editingMiscSale ? 'Edit Misc Sale' : 'Add Misc Sale'" description="Enter payment data and save to database." v-model:open="isOpen"
        :close="{ color: 'error', class: 'rounded-full' }">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-4" @submit="onSubmit">
                <div class="grid grid-cols-2 gap-4">
                    <UFormField label="Amount" required>
                        <UInputNumber v-model="state.amount" class="w-full" :increment="false" :decrement="false"
                            :format-options="{
                                style: 'currency',
                                currency: 'PHP',
                                currencyDisplay: 'code',
                                currencySign: 'accounting'
                            }" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Date" required>
                        <UInput v-model="state.date" type="datetime-local" class="w-full" />
                    </UFormField>
                </div>
                <UFormField label="Reference Number">
                    <UInput v-model="state.referenceNumber" class="w-full" />
                </UFormField>
                <UFormField label="Method" required>
                    <USelect v-model="state.accountId" :items="referenceStore.accountOptions" label-key="name" value-key="id" class="w-full" />
                </UFormField>
                <UFormField label="Description" required>
                    <UTextarea v-model="state.description" class="w-full" />
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