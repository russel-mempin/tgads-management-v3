<script setup lang="ts">
import { reactive, computed, ref, onMounted } from 'vue';
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
import { nowForInput } from '@/utils/formatters.ts';
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
                    :width="state.width" :height="state.height" :unit="state.unit"
                    :quantity="state.quantity" :extras="state.extras"
                    :extra-charge="state.extraCharge" :discount="state.discount" />
                <div class="flex justify-end gap-4">
                    <UButton label="Cancel" />

                    <UButton label="Save" type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>