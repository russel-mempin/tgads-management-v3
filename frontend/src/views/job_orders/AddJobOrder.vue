<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { Customer } from '@/types/customer'
import { getCustomerNames, getCustomerInfo } from '@/api/customers'

// UI Variables
const isWalkIn = ref(false)
const isNewCustomer = ref(false)
const customerList = ref<[string]>([''])
const jobItems = ref<any[]>([])

// Input variables
const joNumber = ref<number | null>(null)
const dateReceived = ref(new Date().toISOString().slice(0, 16))
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

watch(customerNameToSearch, async (name) => {
  if (!name) {
    customerInfo.value = {
      name: '',
      contact_no: '',
      email: '',
      address: '',
      id: '',
    };
    return;
  }
  const exists = customerList.value.some(
    (c) => c.toLowerCase() === name.toLowerCase()
  );
  if (exists) {
    // Autofill from backend
    isNewCustomer.value = false;
    const data = await getCustomerInfo(name);
    if (data) customerInfo.value = data;
  } else {
    // New customer - clear fields and enable input for other info
    isNewCustomer.value = true;
    customerInfo.value = { name, contact_no: '', email: '', address: '', id: '' };
  }
})
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
          :disabled="jobItems.length > 0" :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
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
        <UInputMenu v-model="customerNameToSearch" :items="customerList" placeholder="Search or enter customer name"
          size="lg" class="w-full" :disabled="jobItems.length > 0"
          :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
      </UFormField>
      <div class="mt-6 grid grid-cols-3 gap-6">
        <UFormField label="Contact Number">
          <UInput v-model="customerInfo.contact_no" placeholder="09XX-XXX-XXXX" size="lg" class="w-full"
            :disabled="!isNewCustomer" />
        </UFormField>
        <UFormField label="Email">
          <UInput v-model="customerInfo.email" placeholder="teamgraphicads@yahoo.com" size="lg" class="w-full"
            :disabled="!isNewCustomer" :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
        </UFormField>
        <UFormField label="Address">
          <UInput v-model="customerInfo.address" :items="customerList" placeholder="134 Luzon Ave." size="lg"
            class="w-full" :disabled="!isNewCustomer"
            :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
        </UFormField>
      </div>
    </div>
  </Transition>

  <!-- Footer with Save & Running Totals -->
  <div class="fixed bottom-0 px-6 py-4 w-full shrink-0 border-t border-default backdrop-blur bg-default/80">
    <div class="grid grid-cols-2">
      <div class="flex gap-4 items-center">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Due</p>
          <p class="text-lg font-bold text-highlighted">₱ 99,999.00</p>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Paid</p>
          <p class="text-lg font-bold text-highlighted">₱ 99,999.00</p>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Balance</p>
          <p class="text-lg font-bold text-highlighted">₱ 99,999.00</p>
        </div>
      </div>
      <div class="flex gap-4 items-center">
        <UButton>Back to Job Orders</UButton>
        <UButton>Save</UButton>
      </div>
    </div>
  </div>
</template>