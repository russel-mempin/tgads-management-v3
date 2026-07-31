<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { getAllServices, getAllExtras } from '@/api/services';
import { getUnitPrice } from '@/api/jobOrders';
import type { Service, Extra } from '@/types/service';
import type { JobItemCreate, JobItemExtra, PricingData } from '@/types/jobOrder';
import { nowForInput, utcToInput } from '@/utils/formatters';

const props = defineProps<{
  editingItem?: JobItemCreate | null
}>()

const emit = defineEmits<{
  save: [item: Omit<JobItemCreate, 'item_id'> & { item_id?: string }]
}>()

interface ExtraLineItem {
  extraId: string
  quantity: number
}

const getInitialState = () => {
  return {
    selectedService: '',
    selectedOption: '',
    extras: [] as ExtraLineItem[],
    width: 0,
    height: 0,
    unit: 'ft.',
    quantity: 1,
    jobStatus: 'Pending',
    dueDate: nowForInput(),
    description: '',
    notes: '',
    extraCharge: 0,
    discount: 0,
  }
}

// Data variables
const initial = getInitialState()
const selectedService = ref(initial.selectedService)
const selectedOption = ref(initial.selectedOption)
const extras = ref(initial.extras)
const width = ref(initial.width)
const height = ref(initial.height)
const unit = ref(initial.unit)
const quantity = ref(initial.quantity)
const jobStatus = ref(initial.jobStatus)
const dueDate = ref(initial.dueDate)
const description = ref(initial.description)
const notes = ref(initial.notes)
const extraCharge = ref(initial.extraCharge)
const discount = ref(initial.discount)
const pricingData = ref<PricingData>()


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
const extraTotal = computed(() =>
  extras.value.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const extraChargeTotal = computed(() =>
  extraCharge.value * quantity.value
)
const subtotal = computed(() =>
  ((pricingData.value?.unit_price ?? 0) * quantity.value) + extraTotal.value + extraChargeTotal.value - discount.value
)
const breakdownColumns = computed(() => {
  let cols = 3
  if (isAreaBased.value) cols += 2
  if (extraCharge.value != 0) cols += 1
  return cols
})
let debounceTimer: ReturnType<typeof setTimeout>

// Data Functions
const resetForm = () => {
  const fresh = getInitialState()
  selectedService.value = fresh.selectedService
  selectedOption.value = fresh.selectedOption
  extras.value = fresh.extras
  width.value = fresh.width
  height.value = fresh.height
  unit.value = fresh.unit
  quantity.value = fresh.quantity
  jobStatus.value = fresh.jobStatus
  dueDate.value = fresh.dueDate
  description.value = fresh.description
  notes.value = fresh.notes
  extraCharge.value = fresh.extraCharge
  discount.value = fresh.discount
  pricingData.value = undefined
}
onMounted(async () => {
  serviceList.value = await getAllServices()
  extraList.value = await getAllExtras()
})
watch([width, height, quantity, selectedService, selectedOption, unit], () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (!selectedService.value || !selectedOption.value || !quantity.value) return
    if (isAreaBased.value && (!width.value || !height.value || !unit.value)) return

    pricingData.value = await getUnitPrice({
      height: height.value,
      width: width.value,
      service_id: selectedService.value,
      option_id: selectedOption.value,
      size_unit: unit.value,
      quantity: quantity.value
    })
  }, 400)
})
watch(() => props.editingItem, (item) => {
  if (item) {
    selectedService.value = item.service_id
    selectedOption.value = item.option_id
    extras.value = item.extras.map(e => ({ extraId: e.extra_service_id, quantity: e.quantity }))
    width.value = item.width ?? 0
    height.value = item.height ?? 0
    unit.value = item.size_unit ?? 'ft.'
    quantity.value = item.quantity
    jobStatus.value = item.job_status
    dueDate.value = utcToInput(item.due_date.toISOString())
    description.value = item.description
    notes.value = item.notes
    extraCharge.value = item.extra_charge
    discount.value = item.discount
  }
  else {
    resetForm()
  }
}, { immediate: true })

const handleSave = () => {
  if (!selectedService.value || !selectedOption.value || !quantity.value) return
  if (isAreaBased.value && (!width.value || !height.value)) return

  const payload: Omit<JobItemCreate, 'item_id'> & { item_id?: string } = {
    item_id: props.editingItem?.item_id,
    service_id: selectedService.value,
    option_id: selectedOption.value,
    height: isAreaBased.value ? height.value : undefined,
    width: isAreaBased.value ? width.value : undefined,
    size_unit: isAreaBased.value ? unit.value : undefined,
    quantity: quantity.value,
    job_status: jobStatus.value,
    due_date: new Date(dueDate.value),
    description: description.value,
    notes: notes.value,
    extras: extras.value.map((e): JobItemExtra => {
      const extraData = extraList.value.find(x => x.id === e.extraId)
      return {
        extra_service_id: e.extraId,
        quantity: e.quantity,
        price_snapshot: extraData?.price ?? 0,
        name_snapshot: extraData?.name ?? '',
      }
    }),
    extra_charge: extraCharge.value,
    discount: discount.value,
    unit_price: pricingData.value?.unit_price ?? 0,
    subtotal: subtotal.value,
    service_name_snapshot: selectedServiceData.value?.name ?? '',
    service_option_name_snapshot: applicableOptions.value.find(o => o.id === selectedOption.value)?.name ?? '',
    service_abbreviation_snapshot: selectedServiceData.value?.abbreviation ?? '',
  }

  emit('save', payload)
  resetForm()
  isOpen.value = false
}

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
  <UModal :title="editingItem ? 'Edit Job Item' : 'Add Job Item'" fullscreen description="Describe the item and click add to prepare it for saving."
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
          <UFormField label="Due Date" required>
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

          <div class="bg-muted border-b border-default px-4 py-2 grid"
            :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
            <p v-if="isAreaBased" class="uppercase text-sm">Consumption</p>
            <p v-if="isAreaBased" class="uppercase text-sm">Rate (Based on consumption)</p>
            <p class="uppercase text-sm">Unit Price</p>
            <p v-if="extraCharge != 0" class="uppercase text-sm">Extra Charge Total</p>
            <p class="uppercase text-sm">Extra Total</p>
            <p class="uppercase text-sm">Subtotal</p>
          </div>

          <div class="p-4 grid" :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
            <p v-if="isAreaBased">{{ `${pricingData?.consumption ?? 0} ${pricingData?.consumption_unit ?? unit}.` }}</p>
            <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
            <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
            <p v-if="extraCharge != 0">{{ `₱ ${extraChargeTotal}` }}</p>
            <p>{{ `₱ ${extraTotal}` }}</p>
            <p>₱ {{ subtotal }}</p>
          </div>
        </div>
        <div class="flex justify-end gap-4">
          <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg" class="w-28" />
          <UButton label="Save" icon="i-lucide-save" color="primary" size="lg" class="w-28 font-semibold"
            @click="handleSave" />
        </div>
      </div>
    </template>
  </UModal>
</template>