<script setup lang="ts">
import { ref, onMounted, computed, watchEffect } from 'vue'
import { getAllServices, getAllExtras } from '@/api/services';
import { getUnitPrice } from '@/api/jobOrders';
import type { Service, Extra } from '@/types/service';
import type { PricingData } from '@/types/jobOrder';
import { nowForInput } from '@/utils/formatters';

interface ExtraLineItem {
  extraId: string
  quantity: number
}

// Data variables
const selectedService = ref('')
const selectedOption = ref('')
const extras = ref<ExtraLineItem[]>([])
const width = ref(0)
const height = ref(0)
const unit = ref('ft.')
const quantity = ref(1)
const jobStatus = ref('Pending')
const dueDate = ref(nowForInput())
const description = ref('')
const notes = ref('')
const extraCharge = ref(0)
const discount = ref(0)


// UI Variables
const isOpen = defineModel<boolean>('isOpen', { required: true })
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const selectedServiceData = computed(() =>
  serviceList.value.find(service => service.id === selectedService.value)
)
const applicableOptions = computed(() =>
  selectedServiceData.value?.options ?? []
)
const isAreaBased = computed(() =>
  selectedServiceData.value?.pricing_strategy === 'Area'
)
const unitOptions = ["ft.", "in.", "cm.", "mm.", "meter"]
const statusOptions = ["Pending", "For Layout", "For Approval", "For Printing", "For Pickup", "Released"]
const pricingData = ref<PricingData>()
const extraTotal = computed(() =>
  extras.value.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const extraChargeTotal = computed(() => 
  extraCharge.value * quantity.value
)
const subtotal = computed(() =>
  ((pricingData.value?.unit_price ?? 0) * quantity.value) + extraTotal.value + extraChargeTotal.value - discount.value
)

// Data Functions
onMounted(async () => {
  serviceList.value = await getAllServices()
  extraList.value = await getAllExtras()
})
watchEffect(async () => {
  if (!selectedService.value || !selectedOption.value || !width.value || !height.value || !quantity.value || !unit.value) return
  pricingData.value = await getUnitPrice({
    height: height.value,
    width: width.value,
    service_id: selectedService.value,
    option_id: selectedOption.value,
    size_unit: unit.value,
    quantity: quantity.value
  })
})

// UI Functions
const addExtra = () => {
  extras.value.push({ extraId: '', quantity: 1 })
}
const removeExtra = (index: number) => {
  extras.value.splice(index, 1)
}
const getExtraPrice = (extra: ExtraLineItem) => {
  const extraData = extraList.value.find(x => x.id === extra.extraId)
  if (!extraData) return 0
  return extraData.price * extra.quantity
}
</script>

<template>
  <UModal title="Add Job Item" fullscreen description="Describe the item and click add to prepare it for saving."
    v-model:open="isOpen" :close="{
      color: 'error',
      class: 'rounded-full'
    }">
    <template #body>
      <div class="flex flex-col gap-6">
        <!-- Service Selection -->
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Service/Product" required class="w-full">
            <UInputMenu v-model="selectedService" value-key="id" label-key="name" :items="serviceList" class="w-full" />
          </UFormField>
          <UFormField label="Variant" required class="w-full">
            <UInputMenu v-model="selectedOption" value-key="id" label-key="name" :items="applicableOptions"
              class="w-full" />
          </UFormField>
        </div>
        <!-- Size Input for Area Based -->
        <Transition enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2">
          <div v-if="isAreaBased" class="grid grid-cols-4 gap-6">
            <UFormField label="Width" required class="w-full">
              <UInputNumber v-model="width" :increment="false" :decrement="false" :step="0.1" :step-snapping="false"
                :format-options="{ minimumFractionDigits: 1 }" class="w-full" />
            </UFormField>
            <UFormField label="Height" required class="w-full">
              <UInputNumber v-model="height" :increment="false" :decrement="false" :step="0.1" :step-snapping="false"
                :format-options="{ minimumFractionDigits: 1 }" class="w-full" />
            </UFormField>
            <UFormField label="Unit" required class="w-full">
              <UInputMenu v-model="unit" value-key="id" label-key="name" :items="unitOptions" class="w-full" />
            </UFormField>
            <UFormField label="Quantity" required class="w-full">
              <UInputNumber v-model="quantity" :min="1" class="w-full" />
            </UFormField>
          </div>
        </Transition>
        <!-- Quantity Input for Non Area Based -->
        <Transition enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2">
          <div v-if="!isAreaBased">
            <UFormField label="Quantity" required class="w-full">
              <UInputNumber v-model="quantity" :min="1" class="w-full" />
            </UFormField>
          </div>
        </Transition>
        <!-- Workflow Input -->
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Job Status" class="w-full">
            <UInputMenu v-model="jobStatus" value-key="id" label-key="name" :items="statusOptions" class="w-full" />
          </UFormField>
          <UFormField label="Date Received" required>
            <UInput v-model="dueDate" type="datetime-local" class="w-full" />
          </UFormField>
          <UFormField label="Description" class="w-full">
            <UInput v-model="description" class="w-full" />
          </UFormField>
          <UFormField label="Notes" class="w-full">
            <UInput v-model="notes" class="w-full" />
          </UFormField>
        </div>
        <!-- Extras Selection -->
        <div class="border border-default bg-muted rounded-md">
          <div class="flex items-center justify-between p-4">
            <p class="uppercase font-bold">Extras</p>
            <UButton label="Add Extra" variant="subtle" icon="i-lucide-plus" @click="addExtra" />
          </div>
          <div v-if="!extras.length" class="p-4 text-sm text-muted text-center">
            No extras added.
          </div>
          <div v-for="(extra, index) in extras" :key="index"
            class="grid grid-cols-[1fr_1fr_auto_auto] gap-4 items-end p-4 border-b border-default last:border-b-0">
            <UFormField label="Extra">
              <UInputMenu v-model="extra.extraId" value-key="id" label-key="name" :items="extraList" class="w-full" />
            </UFormField>
            <UFormField label="Quantity">
              <UInputNumber v-model="extra.quantity" :min="1" class="w-full" />
            </UFormField>
            <UFormField label="Price (Auto computed)">
              <UInput :model-value="`₱ ${getExtraPrice(extra)}`" disabled readonly />
            </UFormField>
            <UButton icon="i-lucide-trash-2" color="error" variant="ghost" @click="removeExtra(index)" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra Charge (Per Piece)" class="w-full">
            <UInputNumber v-model="extraCharge" :increment="false" :decrement="false"
              :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
              class="w-full" :step="0.1" :step-snapping="false" />
          </UFormField>
          <UFormField label="Discount (Flat)" class="w-full">
            <UInputNumber v-model="discount" :increment="false" :decrement="false"
              :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
              class="w-full" :step="0.1" :step-snapping="false" />
          </UFormField>
        </div>
        <div class="border border-default rounded-md">
          <p class="bg-elevated p-4 border-b border-default rounded-tl-md rounded-tr-md uppercase font-bold text-sm">
            Pricing Breakdown</p>
          <div class="bg-muted border-b  border-default grid grid-cols-3 px-4 py-2"
            :class="isAreaBased && 'grid-cols-5'">
            <p v-if="isAreaBased" class="uppercase text-sm">Consumption</p>
            <p v-if="isAreaBased" class="uppercase text-sm">Rate (Based on consumption)</p>
            <p class="uppercase text-sm">Unit Price</p>
            <p v-if="extraCharge != 0" class="uppercase text-sm">Extra Charge Total</p>
            <p class="uppercase text-sm">Extra Total</p>
            <p class="uppercase text-sm">Subtotal</p>
          </div>
          <div class="grid grid-cols-3 p-4" :class="isAreaBased && 'grid-cols-5'">
            <p v-if="isAreaBased">{{ `${pricingData?.consumption} ${pricingData?.consumption_unit}.` }}</p>
            <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate}` }}</p>
            <p>{{ `₱ ${pricingData?.unit_price}` }}</p>
            <p>{{ `₱ ${extraTotal}` }}</p>
            <p>₱ {{ subtotal }}</p>
          </div>
        </div>
        <div class="flex justify-end gap-4">
          <UButton label="Cancel" />
          <UButton label="Add" />
        </div>
      </div>
    </template>
  </UModal>
</template>