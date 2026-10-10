<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { z } from 'zod';
import type { Expense, ExpenseCreate } from '@/types/expense';
import { EXPENSE_CATEGORIES } from '@/utils/constants';
import { useReferenceStore } from '@/stores/reference'
import { nowForInput, utcToInput, inputToUtc } from '@/utils/formatters';
import type { FormSubmitEvent } from '@nuxt/ui'

const props = defineProps<{
    editingExpense?: Expense | null
}>()

const emit = defineEmits<{
    save: [Expense: ExpenseCreate]
    close: []
}>()

const referenceStore = useReferenceStore()
const CATEGORY_VALUES = EXPENSE_CATEGORIES
  .filter((category) => category.value !== 'all')
  .map((category) => category.value)

// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const schema = z.object({
    date: z.string().min(1, 'Date is required'),
    category: z.enum(CATEGORY_VALUES),
    description: z.string().min(1, 'Description is required'),
    amount: z.number({ error: 'Amount is required' }).positive('Amount must be greater than 0'),
    accountName: z.string().min(1, 'Payment method is required'),
})
type Schema = z.output<typeof schema>

// Input Variables
const getInitialState = (): Schema => {
    const cashAccount = referenceStore.accountOptions.find(
        a => a.name === 'Cash'
    )
    return {
        date: nowForInput(),
        category: 'Food',
        description: '',
        amount: 0,
        accountName: cashAccount?.id ?? '',
    }
}
const state = reactive<Schema>(getInitialState())

// UI Functions
const resetForm = () => {
    Object.assign(state, getInitialState())
}
const handleCancel = () => {
    isOpen.value = false
    resetForm()
    emit('close')
}

// Data Functions
watch(() => props.editingExpense, (expense) => {
    if (expense) {
        state.date = utcToInput(expense.date)
        state.category = expense.category
        state.description = expense.description
        state.amount = parseFloat(expense.amount)
        state.accountName = expense.account_name ?? ''
    } else {
        resetForm()
    }
}, { immediate: true })

const onSubmit = (event: FormSubmitEvent<Schema>) => {
    const payload: ExpenseCreate = {
        date: inputToUtc(event.data.date),
        category: event.data.category,
        description: event.data.description,
        amount: event.data.amount,
        fund_source: event.data.accountName
    }
    emit('save', payload)
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal 
        :title="editingExpense ? 'Edit Expense' : 'Add Expense'"
        v-model:open="isOpen"
        :close="{ color: 'error', class: 'rounded-full' }"
        description="Enter expense data and click save to save it to the database."
    >
        <template #body>
            <UForm :schema="schema" :state="state" class="flex flex-col gap-6" @submit="onSubmit">
                <div class="grid grid-cols-2 gap-6">
                    <UFormField label="Date" name="date" required class="w-full">
                        <UInput v-model="state.date" type="datetime-local" class="w-full" />
                    </UFormField>
                    <UFormField label="Category" name="category" required class="w-full">
                        <USelect v-model="state.category" :items="CATEGORY_VALUES" class="w-full" />
                    </UFormField>
                </div>
                <UFormField label="Description" name="description" required class="w-full">
                    <UInput v-model="state.description" class="w-full" />
                </UFormField>
                <UFormField label="Amount" name="amount" required class="w-full">
                    <UInputNumber v-model="state.amount" class="w-full" :increment="false" :decrement="false"
                        :format-options="{
                        style: 'currency',
                        currency: 'PHP',
                        currencyDisplay: 'code',
                        currencySign: 'accounting'
                        }" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                </UFormField>
                <UFormField label="Method" name="accountName" required class="w-full">
                    <USelect v-model="state.accountName" class="w-full" value-key="id" label-key="name"
                        :items="referenceStore.accountOptions" />
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