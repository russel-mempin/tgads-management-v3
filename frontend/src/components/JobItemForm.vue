<script setup lang="ts">
import { ref, onMounted, computed, shallowRef } from 'vue'
import { getAllServices, getAllExtras } from '@/api/services';
import type { Service, Extra } from '@/types/service';
import { CalendarDate } from '@internationalized/date'

// Data variables
const selectedService = ref('')
const selectedOption = ref('')
const selectedExtra = ref('')
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
const isAreaBased = computed(() =>
  selectedServiceData.value?.pricing_strategy === 'Area'
)
const unitOptions = ["ft.", "in.", "cm.", "mm.", "meter"]
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Functions
onMounted(async () => {
  serviceList.value = await getAllServices()
  extraList.value = await getAllExtras()
})
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
          <UFormField label="Service/Product" required>
            <UInputMenu v-model="selectedService" value-key="id" label-key="name" :items="serviceList" />
          </UFormField>
          <UFormField label="Variant" required>
            <UInputMenu v-model="selectedOption" value-key="id" label-key="name" :items="applicableOptions" />
          </UFormField>
        </div>
        <Transition enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2">
          <div v-if="isAreaBased" class="grid grid-cols-4 gap-6">
            <UFormField label="Width" required>
              <UInputNumber v-model="width" :increment="false" :decrement="false" />
            </UFormField>
            <UFormField label="Height" required>
              <UInputNumber v-model="height" :increment="false" :decrement="false" />
            </UFormField>
            <UFormField label="Unit" required>
              <UInputMenu v-model="unit" value-key="id" label-key="name" :items="unitOptions" />
            </UFormField>
            <UFormField label="Quantity" required>
              <UInputNumber v-model="quantity" :min="1" />
            </UFormField>
          </div>
        </Transition>
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
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra">
            <UInputMenu v-model="selectedExtra" value-key="id" label-key="name" :items="extraList" />
          </UFormField>
          <UFormField label="Extra Quantity">
            <UInputNumber v-model="extraQuantity" :min="1" />
          </UFormField>
        </div>
        <div>
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
        </div>
        <div class="grid grid-cols-2 gap-6">
          <UFormField label="Extra Charge">
            <UInputNumber v-model="extraCharge" :increment="false" :decrement="false" :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }" />
          </UFormField>
          <UFormField label="Discount">
            <UInputNumber v-model="discount" :increment="false" :decrement="false" :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }" />
          </UFormField>
        </div>
      </div>
    </template>
  </UModal>
</template>