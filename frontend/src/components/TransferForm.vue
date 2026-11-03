<script setup lang="ts">
// Dependency imports
import { reactive } from 'vue';
import { z } from 'zod';
// Component imports
import { useReferenceStore } from '@/stores/reference';
import { nowForInput } from '@/utils/formatters';

const referenceStore = useReferenceStore();

// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true });

// Validation Schema
const schema = z.object({
    referenceNumber: z.string().min(1, 'Reference number is required'),
    transferredAt: z.string().min(1, 'Transfer date is required'),
    description: z.string().min(1, 'Description is required'),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    sourceAccount: z.string().min(1, 'Payment method is required'),
    destinationAccount: z.string().min(1, 'Payment method is required'),
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

const resetForm = () => {
    Object.assign(state, getInitialState())
}
const handleCancel = () => {
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal v-model:open="isOpen" size="md" title="Add Transfer">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-4">
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
                    <UFormField class="flex-1" required label="Source Account">
                        <USelect class="w-full"/>
                    </UFormField>
                    <UFormField class="flex-1" required label="Destination Account">
                        <USelect class="w-full" />
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