<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// --- State ---
const isWalkIn = ref(false)
const customerName = ref('')
const isNewCustomer = ref(false)
const customerInfo = ref({ contact_no: '', email: '', address: '' })
const joNumber = ref<number | null>(null)
const dateReceived = ref(new Date().toISOString().slice(0, 16))
const jobItems = ref<any[]>([])
const payments = ref<any[]>([])
const claims = ref<any[]>([])

// Simulated customer list for demo
const customerSuggestions = ['Pem Sagon', 'Maria Santos', 'Juan dela Cruz', 'Rizal Enterprises']
const filteredCustomers = computed(() =>
  customerName.value
    ? customerSuggestions.filter(c => c.toLowerCase().includes(customerName.value.toLowerCase()))
    : customerSuggestions
)

watch(isWalkIn, (val) => {
  if (val) {
    customerName.value = ''
    customerInfo.value = { contact_no: '', email: '', address: '' }
    isNewCustomer.value = false
  }
})

const totalDue = computed(() =>
  jobItems.value.reduce((sum, item) => sum + (item.subtotal ?? 0), 0)
)
const totalPaid = computed(() =>
  payments.value.reduce((sum, p) => sum + (p.amount ?? 0), 0)
)
const balance = computed(() => totalDue.value - totalPaid.value)
</script>

<template>
  <div class="flex flex-col h-full min-h-0">

    <!-- Page Header -->
    <div class="px-8 pt-8 pb-4 shrink-0">
      <div class="flex items-start justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-primary mb-1">New Entry</p>
          <h1 class="text-2xl font-bold text-highlighted">Add Job Order</h1>
          <p class="text-sm text-muted mt-1">
            Fields marked <span class="text-error font-semibold">*</span> are required.
          </p>
        </div>
        <!-- Walk-in toggle lives here, near the top, prominent -->
        <div class="flex items-center gap-3 bg-elevated border border-default rounded-xl px-4 py-3 mt-1">
          <div>
            <p class="text-sm font-semibold text-highlighted">Walk-in Customer</p>
            <p class="text-xs text-muted">No customer record needed</p>
          </div>
          <UToggle v-model="isWalkIn" size="lg" />
        </div>
      </div>
    </div>

    <!-- Scrollable Form Body -->
    <div class="flex-1 overflow-y-auto min-h-0 px-8 pb-4">

      <!-- SECTION 1: Order Info -->
      <div class="bg-default border border-default rounded-2xl p-6 mb-5">
        <div class="flex items-center gap-2 mb-5">
          <div class="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
            <UIcon name="i-lucide-hash" class="size-3.5 text-inverted" />
          </div>
          <h2 class="font-semibold text-highlighted">Order Information</h2>
        </div>
        <div class="grid grid-cols-2 gap-5">
          <UFormField label="Job Order No." required>
            <UInput v-model="joNumber" type="number" placeholder="e.g. 19291" size="lg" class="w-full"
              :disabled="jobItems.length > 0"
              :hint="jobItems.length > 0 ? 'Clear all job items to change.' : ''" />
          </UFormField>
          <UFormField label="Date Received" required>
            <UInput v-model="dateReceived" type="datetime-local" size="lg" class="w-full" />
          </UFormField>
        </div>
      </div>

      <!-- SECTION 2: Customer (hidden when walk-in) -->
      <Transition enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2">
        <div v-if="!isWalkIn" class="bg-default border border-default rounded-2xl p-6 mb-5">
          <div class="flex items-center gap-2 mb-5">
            <div class="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-user" class="size-3.5 text-inverted" />
            </div>
            <h2 class="font-semibold text-highlighted">Customer</h2>
          </div>

          <UFormField label="Customer Name" required
            hint="Type to search existing customers, or enter a new name.">
            <UInputMenu v-model="customerName" :items="filteredCustomers" size="lg" class="w-full"
              placeholder="Search or enter customer name..." create-option />
          </UFormField>

          <div class="grid grid-cols-2 gap-5 mt-5">
            <UFormField label="Contact No.">
              <UInput v-model="customerInfo.contact_no" placeholder="09XX XXX XXXX" size="lg" class="w-full"
                :disabled="!isNewCustomer" />
            </UFormField>
            <UFormField label="Email Address">
              <UInput v-model="customerInfo.email" placeholder="name@email.com" size="lg" class="w-full"
                :disabled="!isNewCustomer" />
            </UFormField>
          </div>

          <div v-if="isNewCustomer"
            class="mt-4 flex items-center gap-2 text-xs text-primary bg-primary/8 rounded-lg px-3 py-2">
            <UIcon name="i-lucide-user-plus" class="size-3.5 shrink-0" />
            <span>New customer — fill in contact details above.</span>
          </div>
        </div>
      </Transition>

      <!-- Walk-in notice -->
      <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0"
        enter-to-class="opacity-100" leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="isWalkIn"
          class="mb-5 flex items-center gap-3 bg-neutral-100 dark:bg-neutral-800 border border-default rounded-2xl px-5 py-4">
          <UIcon name="i-lucide-user-x" class="size-5 text-muted shrink-0" />
          <p class="text-sm text-muted">Walk-in order — no customer record will be saved.</p>
        </div>
      </Transition>

      <!-- SECTION 3: Job Items -->
      <div class="bg-default border border-default rounded-2xl mb-5 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-default">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-briefcase-business" class="size-3.5 text-inverted" />
            </div>
            <h2 class="font-semibold text-highlighted">Job Items</h2>
            <UBadge v-if="jobItems.length" :label="String(jobItems.length)" variant="soft" size="sm" />
          </div>
          <UButton label="Add Item" icon="i-lucide-plus" size="sm" :disabled="!joNumber"
            :title="!joNumber ? 'Enter a JO Number first' : ''" />
        </div>

        <!-- Empty state -->
        <div v-if="!jobItems.length" class="flex flex-col items-center justify-center py-12 text-center px-6">
          <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-3">
            <UIcon name="i-lucide-package-open" class="size-6 text-muted" />
          </div>
          <p class="font-medium text-highlighted mb-1">No items yet</p>
          <p class="text-sm text-muted">Click "Add Item" to start building this job order.</p>
        </div>

        <!-- Item cards -->
        <div v-else class="divide-y divide-default">
          <div v-for="(item, index) in jobItems" :key="item.item_id ?? index"
            class="px-6 py-4 flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="text-xs font-mono text-muted">{{ item.item_id }}</span>
                <UBadge :label="item.job_status" variant="soft" size="xs" />
              </div>
              <p class="font-medium text-highlighted truncate">
                {{ item.service_name_snapshot }}
                <span v-if="item.service_option_name_snapshot" class="text-muted font-normal"> —
                  {{ item.service_option_name_snapshot }}</span>
              </p>
              <p class="text-sm text-muted mt-0.5">
                {{ item.height }} × {{ item.width }} {{ item.size_unit }} &nbsp;·&nbsp;
                Qty {{ item.quantity }} &nbsp;·&nbsp;
                ₱{{ item.unit_price?.toLocaleString() }}
              </p>
              <div v-if="item.extras?.length" class="mt-1 flex flex-wrap gap-1">
                <span v-for="extra in item.extras" :key="extra.id"
                  class="text-xs bg-elevated text-muted rounded px-2 py-0.5">
                  + {{ extra.name_snapshot }} (₱{{ extra.price_snapshot }})
                </span>
              </div>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <p class="font-semibold text-highlighted">₱{{ item.subtotal?.toLocaleString() }}</p>
              <UButton icon="i-lucide-pen" size="xs" variant="ghost" color="warning" />
              <UButton icon="i-lucide-trash-2" size="xs" variant="ghost" color="error" />
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 4: Payments -->
      <div class="bg-default border border-default rounded-2xl mb-5 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-default">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-banknote-arrow-up" class="size-3.5 text-inverted" />
            </div>
            <h2 class="font-semibold text-highlighted">Payments</h2>
            <UBadge v-if="payments.length" :label="String(payments.length)" variant="soft" size="sm" />
            <span class="text-xs text-muted">(optional)</span>
          </div>
          <UButton label="Add Payment" icon="i-lucide-plus" size="sm" variant="ghost" />
        </div>
        <div v-if="!payments.length" class="px-6 py-5 text-sm text-muted text-center">
          No payments recorded yet.
        </div>
        <div v-else class="divide-y divide-default">
          <div v-for="(p, i) in payments" :key="i" class="px-6 py-3 flex items-center justify-between">
            <div>
              <p class="font-medium text-highlighted">₱{{ p.amount?.toLocaleString() }}</p>
              <p class="text-xs text-muted">{{ p.method }} · {{ p.date_received }}</p>
            </div>
            <UButton icon="i-lucide-trash-2" size="xs" variant="ghost" color="error" />
          </div>
        </div>
      </div>

      <!-- SECTION 5: Claims -->
      <div class="bg-default border border-default rounded-2xl mb-5 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-default">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md bg-primary flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-package-check" class="size-3.5 text-inverted" />
            </div>
            <h2 class="font-semibold text-highlighted">Claiming History</h2>
            <UBadge v-if="claims.length" :label="String(claims.length)" variant="soft" size="sm" />
            <span class="text-xs text-muted">(optional)</span>
          </div>
          <UButton label="Add Claim" icon="i-lucide-plus" size="sm" variant="ghost" />
        </div>
        <div v-if="!claims.length" class="px-6 py-5 text-sm text-muted text-center">
          No claims recorded yet.
        </div>
      </div>

    </div>

    <!-- Sticky Footer -->
    <div class="shrink-0 border-t border-default bg-default/80 backdrop-blur px-8 py-4">
      <div class="flex items-center justify-between gap-6">

        <!-- Running totals -->
        <div class="flex items-center gap-8">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Due</p>
            <p class="text-lg font-bold text-highlighted">₱{{ totalDue.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Total Paid</p>
            <p class="text-lg font-bold text-highlighted">₱{{ totalPaid.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-0.5">Balance</p>
            <p class="text-lg font-bold" :class="balance > 0 ? 'text-warning' : 'text-success'">
              ₱{{ balance.toLocaleString() }}
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <UButton label="Back" variant="outline" color="neutral" icon="i-lucide-arrow-left" size="lg" />
          <UButton label="Save Job Order" icon="i-lucide-save" size="lg" />
        </div>

      </div>
    </div>

  </div>
</template>