<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import type { Customer } from '@/types/customer'
import { getCustomerNames, getCustomerInfo } from '@/api/customers'
import type { JobItemCreate, Payment, ClaimingHistory } from '@/types/jobOrder'
import { formatCurrency, nowForInput } from '@/utils/formatters'

// Components
import JobItemTable from '@/components/JobItemTable.vue'
import PaymentTable from '@/components/PaymentTable.vue'

// UI Variables
const isWalkIn = ref(false)
const isNewCustomer = ref(false)
const isSaving = ref(false)
const customerList = ref<string[]>([''])
const showSuggestions = ref(false)
const jobItems = ref<JobItemCreate[]>([])
const payments = ref<Payment[]>([])
const claimingHistory = ref<ClaimingHistory[]>([])
const totalDue = computed(() =>
    jobItems.value.reduce((sum, item) => sum + item.subtotal, 0)
)
const totalPaid = computed(() =>
    payments.value.reduce((sum, item) => sum + item.amount, 0)
)
const balance = computed(() =>
    totalDue.value - totalPaid.value
)


// Input variables
const joNumber = ref(0)
const dateReceived = ref(nowForInput())
const customerNameToSearch = ref('')
const customerInfo = ref<Customer>({
    name: '',
    contact_no: '',
    email: '',
    address: '',
    id: '',
})

// Functions
onMounted(async () => {
    customerList.value = await getCustomerNames()
})

// Customer related shi
watch(customerNameToSearch, async (name) => {
    if (!name) {
        customerInfo.value = { name: '', contact_no: '', email: '', address: '', id: '' }
        return
    }
    const exists = customerList.value.some(
        (c) => c.toLowerCase() === name.toLowerCase()
    )
    if (exists) {
        isNewCustomer.value = false
        const data = await getCustomerInfo(name)
        if (!data) return
        customerInfo.value = {
            ...data,
            address: data.address?.trim() || 'N/A',
            contact_no: data.contact_no?.trim() || 'N/A',
            email: data.email?.trim() || 'N/A',
        }
    } else {
        isNewCustomer.value = true
        customerInfo.value = { name: name, contact_no: '', email: '', address: '' }
    }
})
const filteredCustomers = computed(() => {
    if (!customerNameToSearch.value) return []
    const q = customerNameToSearch.value.toLowerCase()
    return customerList.value.filter(c => c.toLowerCase().includes(q)).slice(0, 8)
})
const selectCustomer = (name: string) => {
    customerNameToSearch.value = name
    showSuggestions.value = false
}
const handleBlur = () => {
    setTimeout(() => {
        showSuggestions.value = false
    }, 150)
}

const buildPayload = () => {
    const payload = {
        jo_number: joNumber.value,
        date_received: dateReceived.value,
        customerInfo: customerInfo.value,
        job_items: jobItems.value,
        payments: payments.value,
        claiming_history: claimingHistory.value
    }
    handleSave(payload)
}

const handleSave = (payload: any) => {
    console.log(payload)
}
</script>

<template>
    <!-- Page Header -->
    <div class="m-8 shrink-0">
        <div class="flex items-start justify-between">
            <div>
                <p class="text-xs font-semibold uppercase tracking-widest text-primary mb-1">New Entry</p>
                <h1 class="text-2xl font-bold text-highlighted">Add Job Order</h1>
                <p class="text-sm text-muted mt-1">
                    Fields marked <span class="text-error font-semibold">*</span> are required.
                </p>
            </div>
            <div class="flex items-center gap-3 bg-elevated border border-default rounded-md px-4 py-3 mt-1">
                <div>
                    <p class="text-sm font-semibold text-highlighted">Walk-in Customer</p>
                    <p class="text-xs text-muted">No customer record needed</p>
                </div>
                <USwitch v-model="isWalkIn" size="lg" />
            </div>
        </div>
    </div>

    <!-- Order Information -->
    <div class="bg-default border border-default rounded-md p-6 m-8">
        <div class="flex items-center gap-2 mb-6">
            <UIcon name="i-lucide-hash" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
            <h2 class="font-semibold text-highlighted">Order Information</h2>
        </div>
        <div class="grid grid-cols-2 gap-6">
            <UFormField label="Job Order No." required>
                <UInput v-model="joNumber" type="number" placeholder="e.g. 19291" size="lg" class="w-full"
                    :disabled="jobItems.length > 0"
                    :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" 
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()"
                />
            </UFormField>
            <UFormField label="Date Received" required>
                <UInput v-model="dateReceived" type="datetime-local" size="lg" class="w-full" />
            </UFormField>
        </div>
    </div>

    <!-- Customer Selector -->
    <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
        <div v-if="!isWalkIn" class="bg-default border border-default rounded-md p-6 m-8">
            <div class="flex items-center gap-2 mb-8">
                <UIcon name="i-lucide-user" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <h2 class="font-semibold text-highlighted">Customer</h2>
            </div>
            <UFormField label="Name" hint="Type to search existing customers, or enter a new name." required>
                <div class="relative">
                    <UInput v-model="customerNameToSearch" placeholder="Search or enter customer name" size="lg"
                        class="w-full" @focus="showSuggestions = true" @blur="handleBlur" />
                    <div v-if="showSuggestions && filteredCustomers.length"
                        class="absolute z-20 mt-1 w-full bg-default border border-default rounded-md shadow-lg max-h-48 overflow-y-auto">
                        <button v-for="name in filteredCustomers" :key="name" type="button"
                            class="w-full text-left px-3 py-2 hover:bg-elevated text-sm"
                            @mousedown="selectCustomer(name)">
                            {{ name }}
                        </button>
                    </div>
                </div>
            </UFormField>
            <div class="mt-6 grid grid-cols-3 gap-6">
                <UFormField label="Contact Number">
                    <UInput v-model="customerInfo.contact_no" placeholder="09XX-XXX-XXXX" size="lg" class="w-full"
                        :disabled="!isNewCustomer" />
                </UFormField>
                <UFormField label="Email">
                    <UInput v-model="customerInfo.email" placeholder="teamgraphicads@yahoo.com" size="lg" class="w-full"
                        :disabled="!isNewCustomer"
                        :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
                </UFormField>
                <UFormField label="Address">
                    <UInput v-model="customerInfo.address" :items="customerList" placeholder="134 Luzon Ave." size="lg"
                        class="w-full" :disabled="!isNewCustomer"
                        :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
                </UFormField>
            </div>
        </div>
    </Transition>

    <!-- Job Items -->
    <JobItemTable 
        :jo-number="joNumber" 
        :job-items="jobItems" 
        @add-job-item="(item) => jobItems.push(item)"
        @update-job-item="(updated) => {
            const index = jobItems.findIndex(i => i.item_id === updated.item_id)
            if (index !== -1) jobItems[index] = updated
        }" 
        @remove-job-item="(item_id) => jobItems = jobItems.filter(item => item.item_id !== item_id)" 
    />

    <!-- Payments -->
    <PaymentTable
        :balance="balance"
        :payments="payments"
        @add-payment="(payment: Payment) => payments.push(payment)"
        @remove-payment="(ref) => payments = payments.filter(p => p.reference_number !== ref)"
        @update-payment="(index: number, payment: Payment) => payments.splice(index, 1, payment)"
    />

    <!-- Claiming History -->
    <ClaimTable
        :job-items="jobItems"
        :claiming-history="claimingHistory"
        @add-claim="(claim: ClaimingHistory) => claimingHistory.push(claim)"
    />

    <!-- Sticky Bottom Footer with Save & Running Totals -->
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
            <UButton class="w-45 font-bold relative" @click="buildPayload" loading-auto>
                <template #leading>
                    <UIcon v-if="!isSaving" name="i-lucide-save" class="absolute left-3 size-5" />
                </template>
                <span class="w-full text-center">Save</span>
            </UButton>
        </div>
    </div>
</template>