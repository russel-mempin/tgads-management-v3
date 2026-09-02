<script setup lang="ts">
import { reactive } from 'vue'
import { z } from 'zod'

const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const schema = z.object({
    date: z.string().min(1, 'Date is required'),
    referenceNumber: z.string().min(1, 'Reference number is required'),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    accountName: z.string().min(1, 'Payment method is required'),
    description: z.string().optional(),
})
type Schema = z.output<typeof schema>

// Input Variables
const getInitialState = (): Schema => ({
    date: '',
    referenceNumber: '',
    amount: 0,
    accountName: '',
    description: '',
})
const state = reactive<Schema>(getInitialState())
</script>

<template>
    <UModal title="Add Misc Sale" description="Enter payment data and save to database." v-model:open="isOpen"
        :close="{ color: 'error', class: 'rounded-full' }">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-4">
                <div class="grid grid-cols-2 gap-4">
                    <UFormField label="Amount">
                        <UInputNumber v-model="state.amount" class="w-full" :increment="false" :decrement="false"
                            :format-options="{
                                style: 'currency',
                                currency: 'PHP',
                                currencyDisplay: 'code',
                                currencySign: 'accounting'
                            }" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Date">
                        <UInput v-model="state.date" type="datetime-local" class="w-full" />
                    </UFormField>
                </div>
                <UFormField label="Reference Number">
                    <UInput v-model="state.referenceNumber" class="w-full" />
                </UFormField>
                <UFormField label="Method" required>
                    <UTextarea v-model="state.accountName" class="w-full" />
                </UFormField>
                <UFormField label="Description" required>
                    <UTextarea v-model="state.description" class="w-full" />
                </UFormField>
            </UForm>
        </template>
    </UModal>
</template>