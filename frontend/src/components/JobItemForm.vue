<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { getAllServices } from '@/api/services';
import type { Service } from '@/types/service';

// Data variables
const selectedService = ref('')
const selectedOption = ref('')
const width = ref(0)
const height = ref(0)
const quantity = ref(0)


// UI Variables
const serviceList = ref<Service[]>([])
const selectedServiceData = computed(() =>
  serviceList.value.find(service => service.id === selectedService.value)
)
const applicableOptions = computed(() =>
  selectedServiceData.value?.options ?? []
)
const isAreaBased = computed(() =>
  selectedServiceData.value?.pricing_strategy === 'Area'
)
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Functions
onMounted(async () => {
  serviceList.value = await getAllServices()
})
</script>

<template>
  <UModal title="Add Job Item" description="Describe the item and click add to prepare it for saving."
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
              <UInputNumber v-model="width" value-key="id" label-key="name" :items="serviceList" />
            </UFormField>
            <UFormField label="Height" required>
              <UInputNumber v-model="height" value-key="id" label-key="name" :items="applicableOptions" />
            </UFormField>
            <UFormField label="Unit" required>
              <UInputMenu v-model="selectedService" value-key="id" label-key="name" :items="serviceList" />
            </UFormField>
            <UFormField label="Quantity" required>
              <UInputNumber v-model="quantity" value-key="id" label-key="name" :items="applicableOptions" />
            </UFormField>
          </div>
        </Transition>
      </div>
    </template>
  </UModal>
</template>