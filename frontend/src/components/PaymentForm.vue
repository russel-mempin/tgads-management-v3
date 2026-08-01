<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { z } from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import { nowForInput, inputToUtc } from '@/utils/formatters'
import type { AccountOption } from '@/types/account'
import { getAccountOptions } from '@/api/accounts'
import type { Payment } from '@/types/jobOrder'

const emit = defineEmits<{
    addPayment: [payment: Payment]
}>()

// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true })
const accountsList = ref<AccountOption[]>([])

// Validation Schema
const schema = z.object({
    dateReceived: z.string().min(1, 'Date received is required'),
    referenceNumber: z.string().min(1, 'Reference number is required'),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    accountName: z.string().min(1, 'Payment method is required'),
    notes: z.string().optional(),
})
type Schema = z.output<typeof schema>

// Input variables
const getInitialState = (): Schema => ({
    dateReceived: nowForInput(),
    referenceNumber: '',
    amount: 0,
    notes: '',
    accountName: '',
})

const state = reactive<Schema>(getInitialState())

// UI Functions
onMounted(async () => {
    accountsList.value = await getAccountOptions()
    const cashAccount = accountsList.value.find(a => a.name === 'Cash')
    if (cashAccount) {
        state.accountName = cashAccount.id
    }
})
const resetForm = () => {
    Object.assign(state, getInitialState())
}
const handleCancel = () => {
    resetForm()
    isOpen.value = false
}

// Data Functions
const onSubmit = (event: FormSubmitEvent<Schema>) => {
    const selectedAccount = accountsList.value.find(a => a.id === event.data.accountName)

    const payload: Payment = {
        date_received: new Date(inputToUtc(event.data.dateReceived)),
        reference_number: event.data.referenceNumber,
        amount: event.data.amount,
        notes: event.data.notes ?? '',
        account_id: event.data.accountName,
        account_name_snapshot: selectedAccount?.name ?? '',
    }

    emit('addPayment', payload)
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal title="Add Payment" v-model:open="isOpen" :close="{ color: 'error', class: 'rounded-full' }"
        description="Enter payment data and click save to prepare it for saving.">
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-6" @submit="onSubmit">
                <div class="grid grid-cols-2 gap-6">
                    <UFormField label="Date Received" name="dateReceived" required class="w-full">
                        <UInput v-model="state.dateReceived" type="datetime-local" class="w-full" />
                    </UFormField>
                    <UFormField label="Reference No." name="referenceNumber" required class="w-full">
                        <UInput v-model="state.referenceNumber" class="w-full" />
                    </UFormField>
                </div>
                <UFormField label="Amount" name="amount" required class="w-full">
                    <UInputNumber v-model="state.amount" class="w-full" :increment="false" :decrement="false"
                        :format-options="{
                            style: 'currency',
                            currency: 'PHP',
                            currencyDisplay: 'code',
                            currencySign: 'accounting'
                        }" />
                </UFormField>
                <UFormField label="Method" name="accountName" required class="w-full">
                    <UInputMenu v-model="state.accountName" class="w-full" value-key="id" label-key="name"
                        :items="accountsList" />
                </UFormField>
                <UFormField label="Notes" name="notes" class="w-full">
                    <UInput v-model="state.notes" class="w-full" />
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