<script setup lang="ts">
import { reactive, computed, ref, onMounted, watch } from 'vue';
import { z } from 'zod'
// Type imports
import type { JobItemCreate, SizeUnit, JobStatus, JobItemExtraCreate } from '@/types/jobOrder.ts';
import type { Service, Extra } from '@/types/service.ts';
// API call imports
import { getAllServices, getAllExtras } from '@/api/services.ts';
// Component imports
import JobItemServiceFields from './JobItemServiceFields.vue';
import JobItemWorkflowFields from './JobItemWorkflowFields.vue';
import JobItemExtrasFields from './JobItemExtrasFields.vue';
import JobItemPriceAdjustFields from './JobItemPriceAdjustFields.vue';
import JobItemPricingBreakdown from './JobItemPricingBreakdown.vue';
import { nowForInput, utcToInput } from '@/utils/formatters.ts';
import type { FormSubmitEvent } from '@nuxt/ui';

const props = defineProps<{
    editingItem?: JobItemCreate | null
    currentItemIds?: string[]
    joNumber?: number
}>()
const emit = defineEmits<{
    save: [item: JobItemCreate]
}>()
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Validation Schema
const extraSchema = z.object({
    extra_service_id: z.string().min(1, 'Select an extra'),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
})
const schema = z.object({
    selectedService: z.string().min(1, 'Service is required'),
    selectedOption: z.string().min(1, 'Variant is required'),
    width: z.number().optional(),
    height: z.number().optional(),
    unit: z.custom<SizeUnit>().optional(),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
    jobStatus: z.custom<JobStatus>((value) => !!value, {
        message: 'Job status is required'
    }),
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

// Data variables
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])

// Data functions
onMounted(async () => {
    serviceList.value = await getAllServices()
    extraList.value = await getAllExtras()
})
const resetForm = () => {
    Object.assign(state, getInitialState())
    isOpen.value = false
}
const generateItemId = (serviceAbbreviation: string): string => {
    const existingCount = (props.currentItemIds ?? []).filter(
        item => item.includes(`-${serviceAbbreviation}-`)
    ).length
    return `${props.joNumber}-${serviceAbbreviation}-${existingCount + 1}`
}
const selectedServiceData = computed(() =>
    serviceList.value.find(service => service.id === state.selectedService)
)
const isAreaBased = computed(() =>
    selectedServiceData.value?.pricing_strategy === 'Area'
)
// Edit watcher
watch(() => props.editingItem, (item) => {
    console.log("Hi")
    if (item) {
        Object.assign(state, {
            selectedService: item.service_id,
            selectedOption: item.service_option_id,
            extras: item.extras.map(e => ({ extra_service_id: e.extra_service_id, quantity: e.quantity })),
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
// UI variables
const breakdownColumns = computed(() => {
    let cols = 3
    if (isAreaBased) cols += 2
    if (state.extraCharge != 0) cols += 1
    return cols
})
const handleSave = (event: FormSubmitEvent<Schema>) => {
    const d = event.data
    const payload: JobItemCreate = {
        item_id: props.editingItem?.item_id ?? generateItemId(selectedServiceData.value?.abbreviation ?? ''),
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
        extras: d.extras.map((e): JobItemExtraCreate => ({
            extra_service_id: e.extra_service_id,
            quantity: e.quantity,
        })),
        extra_charge: d.extraCharge,
        discount_amount: d.discount,
    }
    emit('save', payload)
    resetForm()
}
</script>

<template>
    <UModal v-model:open="isOpen" :title="editingItem ? 'Edit Job Item' : 'Add Job Item'"
        description="Describe the item and click save to prepare it for saving." :close="{
            color: 'error',
            class: 'rounded-full'
        }" fullscreen>
        <template #body>
            <UForm :schema="schema" :state="state" @submit="handleSave" class="flex flex-col gap-6">
                <JobItemServiceFields :services="serviceList" :selected-service-data="selectedServiceData"
                    :is-area-based="isAreaBased" v-model:service="state.selectedService"
                    v-model:option="state.selectedOption" v-model:width="state.width" v-model:height="state.height"
                    v-model:unit="state.unit" v-model:quantity="state.quantity" />
                <JobItemWorkflowFields v-model:job-status="state.jobStatus" v-model:due-date="state.dueDate"
                    v-model:description="state.description" v-model:notes="state.notes" />
                <JobItemExtrasFields :extra-list="extraList" v-model:extras="state.extras" />
                <JobItemPriceAdjustFields v-model:extra-charge="state.extraCharge" v-model:discount="state.discount" />
                <JobItemPricingBreakdown :selected-service-id="state.selectedService"
                    :selected-option-id="state.selectedOption" :extra-list="extraList" :is-area-based="isAreaBased"
                    :width="state.width" :height="state.height" :unit="state.unit" :quantity="state.quantity"
                    :extras="state.extras" :extra-charge="state.extraCharge" :discount="state.discount">
                    <template #breakdown="{ pricingData, extraTotal, extraChargeTotal, subtotal }">
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
                                <p class="uppercase text-sm">Extras Total</p>
                                <p class="uppercase text-sm">Subtotal</p>
                            </div>

                            <div class="p-4 grid"
                                :style="{ gridTemplateColumns: `repeat(${breakdownColumns}, minmax(0, 1fr))` }">
                                <p v-if="isAreaBased">{{ `${pricingData?.consumption ?? 0}
                                    ${pricingData?.consumption_unit
                                    ?? state.unit}.` }}</p>
                                <p v-if="isAreaBased">{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
                                <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
                                <p v-if="state.extraCharge != 0">{{ `₱ ${state.extraCharge ?? 0 * state.quantity}` }}</p>
                                <p>{{ `₱ ${extraTotal}` }}</p>
                                <p>₱ {{ subtotal }}</p>
                            </div>
                        </div>
                    </template>
                </JobItemPricingBreakdown>
                <div class="flex justify-end gap-4">
                    <UButton label="Cancel" icon="i-lucide-x" variant="outline" size="lg" class="w-40" @click="() => { isOpen = false }" />

                    <UButton label="Save Data" icon="i-lucide-save" size="lg" class="w-40 font-semibold" type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>