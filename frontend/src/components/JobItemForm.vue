<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import { z } from 'zod'
import { nowForInput, utcToInput } from '@/utils/formatters'
import type { Service, Extra } from '@/types/service'
import type { JobItemCreate, JobItemExtra, PricingData } from '@/types/jobOrder'
import type { FormSubmitEvent } from '@nuxt/ui'
import { getAllServices, getAllExtras } from '@/api/services'
import { getUnitPrice } from '@/api/jobOrders'

const props = defineProps<{
    editingItem?: JobItemCreate | null
}>()

const emit = defineEmits<{
    save: [item: Omit<JobItemCreate, 'item_id'> & { item_id?: string }]
}>()

// Validation Schema
interface ExtraLineItem {
    extraId: string
    quantity: number
}
const extraSchema = z.object({
    extraId: z.string().min(1, 'Select an extra'),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
})
const schema = z.object({
    selectedService: z.string().min(1, 'Service is required'),
    selectedOption: z.string().min(1, 'Variant is required'),
    width: z.number().optional(),
    height: z.number().optional(),
    unit: z.string().optional(),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
    jobStatus: z.string().min(1, 'Job status is required'),
    dueDate: z.string().min(1, 'Due date is required'),
    description: z.string().default(''),
    notes: z.string().default(''),
    extras: z.array(extraSchema).default([]),
    extraCharge: z.number().default(0),
    discount: z.number().default(0),
}).superRefine((data, ctx) => {
    // Conditionally require width/height/unit only for area-based services
    if (!isAreaBased.value) return
    if (data.width !== undefined && data.width <= 0) {
        ctx.addIssue({ code: 'custom', path: ['width'], message: 'Width must be greater than 0' })
    }
    if (data.height !== undefined && data.height <= 0) {
        ctx.addIssue({ code: 'custom', path: ['height'], message: 'Height must be greater than 0' })
    }
})
type Schema = z.output<typeof schema>
let debounceTimer: ReturnType<typeof setTimeout>

// Data Variables
const getInitialState = (): Schema => ({
    selectedService: '',
    selectedOption: '',
    width: 0,
    height: 0,
    unit: 'ft.',
    quantity: 1,
    jobStatus: 'Pending',
    dueDate: nowForInput(),
    description: '',
    notes: '',
    extras: [],
    extraCharge: 0,
    discount: 0,
})
const state = reactive<Schema>(getInitialState())
const pricingData = ref<PricingData>()

// UI Variables
const unitOptions = ["ft.", "in.", "cm.", "mm.", "meter"]
const statusOptions = ["Pending", "For Layout", "For Approval", "For Printing", "For Pickup", "Released"]
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const isOpen = defineModel<boolean>('isOpen', { required: true })
const selectedServiceData = computed(() =>
    serviceList.value.find(service => service.id === state.selectedService)
)
const applicableOptions = computed(() =>
    selectedServiceData.value?.options ?? []
)
const isAreaBased = computed(() =>
    selectedServiceData.value?.pricing_strategy === 'Area'
)
const getExtraPrice = (extra: ExtraLineItem) => {
    const extraData = extraList.value.find(x => x.id === extra.extraId)
    if (!extraData) return 0
    return extraData.price * extra.quantity
}
const extraTotal = computed(() =>
    state.extras.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const extraChargeTotal = computed(() =>
    state.extraCharge * state.quantity
)
const subtotal = computed(() =>
    ((pricingData.value?.unit_price ?? 0) * state.quantity) + extraTotal.value + extraChargeTotal.value - state.discount
)
const breakdownColumns = computed(() => {
    let cols = 3
    if (isAreaBased.value) cols += 2
    if (state.extraCharge != 0) cols += 1
    return cols
})

// Data functions
const resetForm = () => {
    Object.assign(state, getInitialState())
    pricingData.value = undefined
}
onMounted(async () => {
    serviceList.value = await getAllServices()
    extraList.value = await getAllExtras()
})
// Pricing watcher
watch(
    () => [state.width, state.height, state.quantity, state.selectedService, state.selectedOption, state.unit],
    () => {
        clearTimeout(debounceTimer)
        debounceTimer = setTimeout(async () => {
            if (!state.selectedService || !state.selectedOption || !state.quantity) return
            if (isAreaBased.value && (!state.width || !state.height || !state.unit)) return

            pricingData.value = await getUnitPrice({
                height: state.height ?? 0,
                width: state.width ?? 0,
                service_id: state.selectedService,
                option_id: state.selectedOption,
                size_unit: state.unit ?? 'ft.',
                quantity: state.quantity
            })
        }, 400)
    }
)
// Edit watcher
watch(() => props.editingItem, (item) => {
    if (item) {
        Object.assign(state, {
            selectedService: item.service_id,
            selectedOption: item.service_option_id,
            extras: item.extras.map(e => ({ extraId: e.extra_service_id, quantity: e.quantity })),
            width: item.width ?? 0,
            height: item.height ?? 0,
            unit: item.size_unit ?? 'ft.',
            quantity: item.quantity,
            jobStatus: item.job_status,
            dueDate: utcToInput(item.due_date.toISOString()),
            description: item.description,
            notes: item.notes,
            extraCharge: item.extra_charge,
            discount: item.discount_amount,
        })
    } else {
        resetForm()
    }
}, { immediate: true })

// Reset on close
watch(isOpen, (open) => {
    if (!open) resetForm()
})
const onSubmit = (event: FormSubmitEvent<Schema>) => {
    const d = event.data
    const payload: Omit<JobItemCreate, 'item_id'> & { item_id?: string } = {
        item_id: props.editingItem?.item_id,
        service_id: d.selectedService,
        service_option_id: d.selectedOption,
        height: isAreaBased.value ? d.height : undefined,
        width: isAreaBased.value ? d.width : undefined,
        size_unit: isAreaBased.value ? d.unit : undefined,
        quantity: d.quantity,
        job_status: d.jobStatus,
        due_date: new Date(d.dueDate),
        description: d.description,
        notes: d.notes,
        extras: d.extras.map((e): JobItemExtra => {
            const extraData = extraList.value.find(x => x.id === e.extraId)
            return {
                extra_service_id: e.extraId,
                quantity: e.quantity,
                price_snapshot: extraData?.price ?? 0,
                name_snapshot: extraData?.name ?? '',
            }
        }),
        extra_charge: d.extraCharge,
        discount_amount: d.discount,
        unit_price: pricingData.value?.unit_price ?? 0,
        subtotal: subtotal.value,
        service_name_snapshot: selectedServiceData.value?.name ?? '',
        service_option_name_snapshot: applicableOptions.value.find(o => o.id === d.selectedOption)?.name ?? '',
        service_abbreviation_snapshot: selectedServiceData.value?.abbreviation ?? '',
    }

    emit('save', payload)
    resetForm()
    isOpen.value = false
}

// UI Functions
const addExtra = () => {
    state.extras.push({ extraId: '', quantity: 1 })
}
const removeExtra = (index: number) => {
    state.extras.splice(index, 1)
}
</script>

<template>
    <UModal :title="editingItem ? 'Edit Job Item' : 'Add Job Item'" fullscreen
        description="Describe the item and click save to prepare it for saving." v-model:open="isOpen" :close="{
            color: 'error',
            class: 'rounded-full'
        }">
        <template #body>
            <UForm :schema="schema" :state="state" @submit="onSubmit" class="flex flex-col gap-6">
                <div class="flex flex-col gap-6">
                    <!-- Service Selection -->
                    <div class="grid grid-cols-2 gap-6">
                        <UFormField label="Service/Product" name="selectedService" required class="w-full">
                            <UInputMenu v-model="state.selectedService" value-key="id" label-key="name"
                                :items="serviceList" class="w-full" />
                        </UFormField>
                        <UFormField label="Variant" name="selectedOption" required class="w-full">
                            <USelect v-model="state.selectedOption" value-key="id" label-key="name"
                                :items="applicableOptions" class="w-full" />
                        </UFormField>
                    </div>
                    <!-- Size Input for Area Based -->
                    <Transition enter-active-class="transition-all duration-300 ease-out"
                        enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
                        leave-active-class="transition-all duration-200 ease-in"
                        leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
                        <div v-if="isAreaBased" class="grid grid-cols-4 gap-6">
                            <UFormField label="Width" name="width" required class="w-full">
                                <UInputNumber v-model="state.width" :increment="false" :decrement="false" :step="0.1"
                                    :step-snapping="false" :format-options="{ minimumFractionDigits: 1 }" class="w-full"
                                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                            </UFormField>
                            <UFormField label="Height" name="height" required class="w-full">
                                <UInputNumber v-model="state.height" :increment="false" :decrement="false" :step="0.1"
                                    :step-snapping="false" :format-options="{ minimumFractionDigits: 1 }" class="w-full"
                                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                            </UFormField>
                            <UFormField label="Unit" name="unit" required class="w-full">
                                <UInputMenu v-model="state.unit" value-key="id" label-key="name" :items="unitOptions"
                                    class="w-full" />
                            </UFormField>
                            <UFormField label="Quantity" required class="w-full">
                                <UInputNumber v-model="state.quantity" :min="1" class="w-full"
                                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                            </UFormField>
                        </div>
                    </Transition>
                    <!-- Quantity Input for Non Area Based -->
                    <Transition enter-active-class="transition-all duration-300 ease-out"
                        enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
                        leave-active-class="transition-all duration-200 ease-in"
                        leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
                        <div v-if="!isAreaBased">
                            <UFormField label="Quantity" required class="w-full">
                                <UInputNumber v-model="state.quantity" :min="1" class="w-full"
                                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                            </UFormField>
                        </div>
                    </Transition>
                    <!-- Workflow Input -->
                    <div class="grid grid-cols-2 gap-6">
                        <UFormField label="Job Status" class="w-full">
                            <USelect v-model="state.jobStatus" value-key="id" label-key="name" :items="statusOptions"
                                class="w-full" />
                        </UFormField>
                        <UFormField label="Due Date" required>
                            <UInput v-model="state.dueDate" type="datetime-local" class="w-full" />
                        </UFormField>
                        <UFormField label="Description" class="w-full">
                            <UInput v-model="state.description" class="w-full" />
                        </UFormField>
                        <UFormField label="Notes" class="w-full">
                            <UInput v-model="state.notes" class="w-full" />
                        </UFormField>
                    </div>
                    <!-- Extras Selection -->
                    <div class="border border-default bg-muted rounded-md">
                        <div class="flex items-center justify-between p-4">
                            <p class="uppercase font-bold">Extras</p>
                            <UButton label="Add Extra" variant="subtle" icon="i-lucide-plus" @click="addExtra" />
                        </div>
                        <div v-if="!state.extras.length" class="p-4 text-sm text-muted text-center">
                            No extras added.
                        </div>
                        <div v-for="(extra, index) in state.extras" :key="index"
                            class="grid grid-cols-[1fr_1fr_auto_auto] gap-4 items-end p-4 border-b border-default last:border-b-0">
                            <UFormField label="Extra">
                                <USelect v-model="extra.extraId" value-key="id" label-key="name" :items="extraList"
                                    class="w-full" />
                            </UFormField>
                            <UFormField label="Quantity">
                                <UInputNumber v-model="extra.quantity" :min="1" class="w-full" />
                            </UFormField>
                            <UFormField label="Price (Auto computed)">
                                <UInput :model-value="`₱ ${getExtraPrice(extra)}`" disabled readonly />
                            </UFormField>
                            <UButton icon="i-lucide-trash-2" color="error" variant="ghost"
                                @click="removeExtra(index)" />
                        </div>
                    </div>
                    <!-- Extra Charge / Discount -->
                    <div class="grid grid-cols-2 gap-6">
                        <UFormField label="Extra Charge (Per Piece)" class="w-full">
                            <UInputNumber v-model="state.extraCharge" :increment="false" :decrement="false"
                                :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                                class="w-full" :step="0.1" :step-snapping="false" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                        </UFormField>
                        <UFormField label="Discount (Flat)" class="w-full">
                            <UInputNumber v-model="state.discount" :increment="false" :decrement="false"
                                :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                                class="w-full" :step="0.1" :step-snapping="false" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                        </UFormField>
                    </div>
                    <!-- Pricing Breakdown -->
                    <div class="border border-default rounded-md">
                        <p
                            class="bg-elevated p-4 border-b border-default rounded-tl-md rounded-tr-md uppercase font-bold text-sm">
                            Pricing Breakdown</p>

                        <div class="bg-muted border-b border-default px-4 py-2 grid"
                            :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
                            <p v-if="isAreaBased" class="uppercase text-sm">Consumption</p>
                            <p v-if="isAreaBased" class="uppercase text-sm">Rate (Based on consumption)</p>
                            <p class="uppercase text-sm">Unit Price</p>
                            <p v-if="state.extraCharge != 0" class="uppercase text-sm">Extra Charge Total</p>
                            <p class="uppercase text-sm">Extra Total</p>
                            <p class="uppercase text-sm">Subtotal</p>
                        </div>

                        <div class="p-4 grid"
                            :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
                            <p v-if="isAreaBased">{{ `${pricingData?.consumption ?? 0} ${pricingData?.consumption_unit
                                ?? state.unit}.` }}</p>
                            <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
                            <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
                            <p v-if="state.extraCharge != 0">{{ `₱ ${extraChargeTotal}` }}</p>
                            <p>{{ `₱ ${extraTotal}` }}</p>
                            <p>₱ {{ subtotal }}</p>
                        </div>
                    </div>
                    <!-- Cancel / Save Buttons -->
                    <div class="flex justify-end gap-4">
                        <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg"
                            class="w-28" @click="() => { isOpen = false }" />
                        <UButton label="Save" icon="i-lucide-save" color="primary" size="lg" class="w-28 font-semibold"
                            type="submit" />
                    </div>
                </div>
            </UForm>
        </template>
    </UModal>
</template>