<script setup lang="ts">
// Dependency imports
import { reactive, watch } from 'vue';
import { z } from 'zod';
import type { FormSubmitEvent } from '@nuxt/ui';
// Component imports
import { useReferenceStore } from '@/stores/reference';
import { nowForInput, inputToUtc, utcToInput } from '@/utils/formatters';
// Type imports 
import type { Transfer, TransferCreate } from '@/types/transfer';

const referenceStore = useReferenceStore();

const props = defineProps<{
    editingTransfer?: Transfer | null
}>()
const emit = defineEmits<{
    save: [transfer: TransferCreate]
}>()

// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true });

// Validation Schema
const schema = z.object({
    referenceNumber: z.string().min(1, 'Reference number is required'),
    transferredAt: z.string().min(1, 'Transfer date is required'),
    description: z.string().min(1, 'Description is required'),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    sourceAccount: z.string().min(1, 'Source account is required'),
    destinationAccount: z.string().min(1, 'Destination account is required'),
}).superRefine((data, ctx) => {
    if (
        data.sourceAccount &&
        data.destinationAccount &&
        data.sourceAccount === data.destinationAccount
    ) {
        ctx.addIssue({
            code: 'custom',
            message: 'Source and destination accounts cannot be the same',
            path: ['destinationAccount'],
        })
    }
})
type Schema = z.output<typeof schema>
// Input variables
const getInitialState = (): Schema => {
    const rcbcOld = referenceStore.accountOptions.find(
        a => a.name === 'RCBC Old'
    )
    return {
        referenceNumber: '',
        transferredAt: nowForInput(),
        description: '',
        amount: 0,
        sourceAccount: rcbcOld?.id ?? '',
        destinationAccount: '',
    }
}
const state = reactive<Schema>(getInitialState())

// Data Functions
const resetForm = () => {
    Object.assign(state, getInitialState())
}
const handleCancel = () => {
    resetForm()
    isOpen.value = false
}

watch(() => props.editingTransfer, (transfer) => {
    if (transfer) {
        state.referenceNumber = transfer.reference_number ?? ''
        state.transferredAt = utcToInput(transfer.transferred_at)
        state.description = transfer.description ?? ''
        state.amount = Number(transfer.amount)
        state.sourceAccount = transfer.source_account_name
        state.destinationAccount = transfer.destination_account_name
    }
    else {
        resetForm()
    }
}, { immediate: true })

const onSubmit = (event: FormSubmitEvent<Schema>) => {
    const payload: TransferCreate = {
        transferred_at: inputToUtc(event.data.transferredAt),
        description: event.data.description,
        reference_number: event.data.referenceNumber,
        amount: event.data.amount,
        source_account_id: event.data.sourceAccount,
        destination_account_id: event.data.destinationAccount,
    }
    emit('save', payload)
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal v-model:open="isOpen" size="md" :title="props.editingTransfer ? 'Edit Transfer' : 'Add Transfer'" description="Enter transfer details and click Save."
        :close="{ color: 'error', class: 'rounded-full' }">
        <template #body>
            <UForm :schema="schema" :state="state" @submit="onSubmit" class="flex flex-col gap-4">
                <UFormField label="Reference No." name="referenceNumber" required class="w-full">
                    <UInput v-model="state.referenceNumber" class="w-full" />
                </UFormField>
                <UFormField label="Transfer Date" required>
                    <UInput v-model="state.transferredAt" type="datetime-local" class="w-full" />
                </UFormField>
                <UFormField label="Description" required>
                    <UTextarea v-model="state.description" class="w-full" />
                </UFormField>
                <UFormField label="Amount" required>
                    <UInputNumber v-model="state.amount" class="w-full" :increment="false" :decrement="false"
                        :format-options="{
                            style: 'currency',
                            currency: 'PHP',
                            currencyDisplay: 'code',
                            currencySign: 'accounting'
                        }" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                </UFormField>
                <div class="grid grid-cols-2 items-center justify-between gap-4">
                    <UFormField class="flex-1" required label="Source Account" name="sourceAccount">
                        <USelect v-model="state.sourceAccount" class="w-full" :items="referenceStore.accountOptions"
                            label-key="name" value-key="id" />
                    </UFormField>

                    <UFormField class="flex-1" required label="Destination Account" name="destinationAccount">
                        <USelect v-model="state.destinationAccount" class="w-full"
                            :items="referenceStore.accountOptions" label-key="name" value-key="id" />
                    </UFormField>
                </div>
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