<script setup lang="ts">
import { ref, onMounted, computed, shallowRef, watch } from 'vue'
import { getAllServices, getAllExtras } from '@/api/services';
import type { Service, Extra } from '@/types/service';
import { CalendarDate } from '@internationalized/date'

interface ExtraLineItem {
  extraId: string
  quantity: number
}

// Data variables
const selectedService = ref('')
const selectedOption = ref('')
const extras = ref<ExtraLineItem[]>([{ extraId: '', quantity: 1 }])
const width = ref(0)
const height = ref(0)
const unit = ref('ft')
const quantity = ref(1)
const extraQuantity = ref(1)
const dueDate = shallowRef(new CalendarDate(2022, 2, 3))
const description = ref('')
const notes = ref('')
const extraCharge = ref(0)
const discount = ref(0)


// UI Variables
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const selectedServiceData = computed(() =>
  serviceList.value.find(service => service.id === selectedService.value)
)
const applicableOptions = computed(() =>
  selectedServiceData.value?.options ?? []
)
const selectedOptionData = computed(() =>
  applicableOptions.value.find(option => option.id === selectedOption.value)
)
const isAreaBased = computed(() =>
  selectedServiceData.value?.pricing_strategy === 'Area'
)
const unitOptions = ["ft.", "in.", "cm.", "mm.", "meter"]
const isOpen = defineModel<boolean>('isOpen', { required: true })
const area = computed(() =>
  width.value * height.value
)
const consumption = computed(() =>
  isAreaBased.value ? area.value * quantity.value : quantity.value
)
const rate = computed(() => {
  const tiers = selectedOptionData.value?.price_tiers
  if (!tiers || !tiers.length) return 0

  const matchingTier = [...tiers]
    .sort((a, b) => a.min_threshold - b.min_threshold)
    .reverse()
    .find(tier => consumption.value >= tier.min_threshold)

  return matchingTier?.rate ?? 0
})

// Functions
onMounted(async () => {
  serviceList.value = await getAllServices()
  extraList.value = await getAllExtras()
})
watch([width, height, quantity, selectedService, selectedOption], async () => {
    if (!selectedService.value || !selectedOption.value || !width.value || !height.value || !quantity.value) return
    alert("CALL API")
  }
)
</script>

<template>
  <UModal title="Add Job Item" fullscreen description="Describe the item and click add to prepare it for saving."
    v-model:open="isOpen" :close="{
      color: 'error',
      class: 'rounded-full'
    }">
    <template #body>
      <div class="flex flex-col gap-6">
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Service/Product" required class="w-full">
            <UInputMenu v-model="selectedService" value-key="id" label-key="name" :items="serviceList" class="w-full" />
          </UFormField>
          <UFormField label="Variant" required class="w-full">
            <UInputMenu v-model="selectedOption" value-key="id" label-key="name" :items="applicableOptions" class="w-full" />
          </UFormField>
        </div>
        <Transition enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2">
          <div v-if="isAreaBased" class="grid grid-cols-4 gap-6">
            <UFormField label="Width" required>
              <UInputNumber v-model="width" :increment="false" :decrement="false" :step="0.1" :step-snapping="false"
                :format-options="{ minimumFractionDigits: 1 }" />
            </UFormField>
            <UFormField label="Height" required>
              <UInputNumber v-model="height" :increment="false" :decrement="false" :step="0.1" :step-snapping="false"
                :format-options="{ minimumFractionDigits: 1 }" />
            </UFormField>
            <UFormField label="Unit" required>
              <UInputMenu v-model="unit" value-key="id" label-key="name" :items="unitOptions" />
            </UFormField>
            <UFormField label="Quantity" required>
              <UInputNumber v-model="quantity" :min="1" />
            </UFormField>
          </div>
        </Transition>
        <Transition enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2">
          <div v-if="!isAreaBased" class="grid grid-cols-4 gap-6">
            <UFormField label="Quantity" required>
              <UInputNumber v-model="quantity" :min="1" />
            </UFormField>
          </div>
        </Transition>
        <div class="border border-default rounded-md">
          <div class="flex items-center justify-between p-4">
            <p>Extras</p>
            <UButton label="Add Extra" variant="subtle" />
          </div>
        </div>
        <!-- <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra">
            <UInputMenu v-model="selectedExtra" value-key="id" label-key="name" :items="extraList" />
          </UFormField>
          <UFormField label="Extra Quantity">
            <UInputNumber v-model="extraQuantity" :min="1" />
          </UFormField>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra">
            <UInputMenu v-model="selectedExtra" value-key="id" label-key="name" :items="extraList" />
          </UFormField>
          <UFormField label="Extra Quantity">
            <UInputNumber v-model="extraQuantity" :min="1" />
          </UFormField>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra">
            <UInputMenu v-model="selectedExtra" value-key="id" label-key="name" :items="extraList" />
          </UFormField>
          <UFormField label="Extra Quantity">
            <UInputNumber v-model="extraQuantity" :min="1" />
          </UFormField>
        </div>
        <div class="grid grid-cols-4 gap-6">
          <UFormField label="Job Status">
            <UInputMenu v-model="selectedExtra" value-key="id" label-key="name" :items="extraList" />
          </UFormField>
          <UFormField label="Due Date">
            <UInputDate v-model="dueDate" />
          </UFormField>
          <UFormField label="Description">
            <UInput v-model="description" />
          </UFormField>
          <UFormField label="Notes">
            <UInput v-model="notes" />
          </UFormField>
        </div> -->
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra Charge">
            <UInputNumber v-model="extraCharge" :increment="false" :decrement="false"
              :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }" />
          </UFormField>
          <UFormField label="Discount">
            <UInputNumber v-model="discount" :increment="false" :decrement="false"
              :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }" />
          </UFormField>
        </div>
        <div class="border border-default rounded-md">
          <p class="bg-elevated p-4 border-b border-default rounded-tl-md rounded-tr-md uppercase font-bold text-sm">
            Pricing Breakdown</p>
          <div class="bg-muted border-b  border-default grid grid-cols-4 px-3 py-2"
            :class="isAreaBased && 'grid-cols-4'">
            <p v-if="isAreaBased" class="uppercase text-sm">Consumption</p>
            <p class="uppercase text-sm">{{ `Rate ${isAreaBased && '(Based on consumption)'}` }}</p>
            <p class="uppercase text-sm">Extra Total</p>
            <p class="uppercase text-sm">Subtotal</p>
          </div>
          <div class="grid grid-cols-4 p-4" :class="isAreaBased && 'grid-cols-4'">
            <p v-if="isAreaBased">{{ `${area * quantity} sq${unit}` }}</p>
            <p>{{ `₱ ${rate}` }}</p>
            <p>extra_price</p>
            <p>unit price * quantity</p>
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