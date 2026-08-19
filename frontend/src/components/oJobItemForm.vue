<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import { z } from 'zod'
import { nowForInput, utcToInput } from '@/utils/formatters'
import type { Service, Extra } from '@/types/service'
import type { JobItemCreate, JobItemExtraCreate, PricingData, SizeUnit, JobStatus } from '@/types/jobOrder'
import type { FormSubmitEvent } from '@nuxt/ui'
import { getAllServices, getAllExtras } from '@/api/services'
import { getUnitPrice } from '@/api/jobOrders'

const props = defineProps<{
    editingItem?: JobItemCreate | null
    currentItemIds?: string[]
    joNumber?: number
}>()

const isOpen = defineModel<boolean>('isOpen', { required: true })

const emit = defineEmits<{
    save: [item: JobItemCreate]
}>()

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
let debounceTimer: ReturnType<typeof setTimeout>

// Data Variables
const getInitialState = (): Schema => ({
    selectedService: '',
    selectedOption: '',
    width: 0,
    height: 0,
    unit: 'FEET',
    quantity: 1,
    jobStatus: 'PENDING',
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
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])
const selectedServiceData = computed(() =>
    serviceList.value.find(service => service.id === state.selectedService)
)
const isAreaBased = computed(() =>
    selectedServiceData.value?.pricing_strategy === 'Area'
)

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

// Reset on close
watch(isOpen, (open) => {
    if (!open) resetForm()
})
const generateItemId = (serviceAbbreviation: string): string => {
    const existingCount = (props.currentItemIds ?? []).filter(
        item => item.includes(`-${serviceAbbreviation}-`)
    ).length
    return `${props.joNumber}-${serviceAbbreviation}-${existingCount + 1}`
}
const onSubmit = async (event: FormSubmitEvent<Schema>) => {
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
    isOpen.value = false
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
                    <!-- Extra Charge / Discount -->
                    <!-- Pricing Breakdown -->
            
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