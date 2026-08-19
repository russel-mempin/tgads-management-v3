<script setup lang="ts">
// Framework/Library imports
import { reactive, watch, ref, computed, onMounted } from 'vue';
import { z } from 'zod'
import isEqual from 'lodash/isEqual'
// Type imports
import type { JobItem } from '@/types/jobOrder';
import type { FormSubmitEvent } from '@nuxt/ui';
import type { Service, Extra } from '@/types/service'
// API call imports
import { getAllServices, getAllExtras } from '@/api/services';
// Component imports
import JobItemExtrasFields from './job-item-form/JobItemExtrasFields.vue';
import JobItemPriceAdjustFields from './job-item-form/JobItemPriceAdjustFields.vue';
import JobItemPricingBreakdown from './job-item-form/JobItemPricingBreakdown.vue';

const emit = defineEmits<{
    submit: [payload: {
        id: string
        changes: Partial<JobItem>
    }]
}>()

const props = defineProps<{
    jobItem: JobItem
}>()
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Form schemas
const extraSchema = z.object({
    extra_service_id: z.string().min(1, 'Select an extra'),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
})
const schema = z.object({
    quantity: z.number().min(1, 'Quantity must be at least 1'),
    job_status: z.string().min(1, 'Job status is required'),
    notes: z.string().default(''),
    extra_charge: z.number().default(0),
    discount_amount: z.number().default(0),
    extras: z.array(extraSchema).default([])
})
type Schema = z.output<typeof schema>
const form = reactive<Schema>({
    quantity: 1,
    job_status: '',
    notes: '',
    extra_charge: 0,
    discount_amount: 0,
    extras: []
})

// Data variables
const serviceList = ref<Service[]>([])
const extraList = ref<Extra[]>([])

// UI Variables
const statusOptions = ["Pending", "For Layout", "For Approval", "For Printing", "For Pickup", "Released", "Cancelled"]
const selectedServiceData = computed(() =>
    serviceList.value.find(service => service.id === props.jobItem.service_id)
)
const isAreaBased = computed(() =>
    selectedServiceData.value?.pricing_strategy === 'Area'
)

// Data functions
onMounted(async () => {
    serviceList.value = await getAllServices()
    extraList.value = await getAllExtras()
})
// Put data to form
watch(
    () => props.jobItem,
    (item) => {
        if (!item) return

        form.quantity = item.quantity
        form.job_status = item.job_status
        form.notes = item.notes ?? ''
        form.extra_charge = item.extra_charge ?? 0
        form.discount_amount = item.discount_amount ?? 0

        form.extras = (item.extras ?? []).map(extra => ({
            extra_service_id: extra.extra_service_id,
            quantity: extra.quantity,
        }))
    },
    { immediate: true }
)

const getChanges = (): Record<string, unknown> => {
    if (!props.jobItem) return {}

    const changes: Record<string, unknown> = {}

    for (const key of Object.keys(form) as (keyof typeof form)[]) {
        const current = key === 'extras'
            ? form.extras.map(e => ({ extra_service_id: e.extra_service_id, quantity: e.quantity }))
            : form[key]

        const original = key === 'extras'
            ? props.jobItem.extras ?? []
            : props.jobItem[key as keyof typeof props.jobItem]

        if (!isEqual(current, original)) {
            changes[key] = current
        }
    }

    return changes
}

const onSubmit = (event: FormSubmitEvent<Schema>) => {
    if (!props.jobItem) return

    const changes = getChanges()

    if (Object.keys(changes).length === 0) {
        isOpen.value = false
        return
    }

    emit('submit', {
        id: props.jobItem.id,
        changes,
    })
}
</script>

<template>
    <UModal :ui="{ content: 'max-w-2xl' }" title="Edit Job Item" description="Update job item info when saved."
        v-model:open="isOpen" :close="{ color: 'error', class: 'rounded-full' }">
        <template #body>
            <UForm :schema="schema" :state="form" @submit="onSubmit" class="flex flex-col gap-4">
                <div class="grid grid-cols-2 gap-4">
                    <UFormField label="Quantity" name="quantity" required class="w-full">
                        <UInputNumber v-model="form.quantity" :min="1" class="w-full"
                            @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Job Status" name="job_status" required class="w-full">
                        <USelect v-model="form.job_status" value-key="id" label-key="name" :items="statusOptions"
                            class="w-full" />
                    </UFormField>
                </div>
                <UFormField label="Notes" name="notes" class="w-full">
                    <UInput v-model="form.notes" class="w-full" />
                </UFormField>
                <JobItemExtrasFields :extra-list="extraList" v-model:extras="form.extras" />
                <JobItemPriceAdjustFields v-model:extra-charge="form.extra_charge"
                    v-model:discount="form.discount_amount" />
                <!-- Pricing Breakdown -->
                <JobItemPricingBreakdown :selected-service-id="jobItem?.service_id"
                    :selected-option-id="jobItem.service_option_id" :extra-list="extraList" :is-area-based="isAreaBased"
                    :width="jobItem.width" :height="jobItem.height" :unit="jobItem.size_unit" :quantity="form.quantity"
                    :extras="form.extras" :extra-charge="form.extra_charge" :discount="form.discount_amount">
                    <template #breakdown="{ pricingData, extraTotal, extraChargeTotal, subtotal }">
                        <div>
                            <p
                                class="bg-elevated p-2 border border-default rounded-tl-md rounded-tr-md uppercase font-bold text-sm">
                                Pricing Breakdown</p>
                            <div v-if="jobItem?.width && jobItem?.height && jobItem?.size_unit"
                                class="border-r border-b border-l border-default px-2 py-1 flex items-center justify-between">
                                <p class="uppercase text-sm">Dimensions</p>
                                <p>{{ `${jobItem?.width} × ${jobItem?.height} ${jobItem?.size_unit}` }}</p>
                            </div>
                            <div v-if="jobItem?.width && jobItem?.height && jobItem?.size_unit"
                                class="border-r border-b border-l border-default px-2 py-1 flex items-center justify-between">
                                <p class="uppercase text-sm">Extras Total</p>
                                <p>{{ `₱ ${extraTotal}` }}</p>
                            </div>
                            <div class="border-r border-b border-l border-default px-2 py-1 grid grid-cols-2 gap-2">
                                <div>
                                    <p class="uppercase text-sm">Consumption</p>
                                    <p>{{ `${pricingData?.consumption} ${pricingData?.consumption_unit}.` }}</p>
                                </div>
                                <div>
                                    <p class="uppercase text-sm">Rate</p>
                                    <p>{{ `₱ ${pricingData?.rate ?? 0}` }}</p>
                                </div>
                                <div>
                                    <p class="uppercase text-sm">Unit Price</p>
                                    <p>{{ `₱ ${pricingData?.unit_price ?? 0}` }}</p>
                                </div>
                                <div>
                                    <p class="uppercase text-sm">Extra Charge Total</p>
                                    <p>{{ `₱ ${extraChargeTotal}` }}</p>
                                </div>
                            </div>
                            <div
                                class="border-r border-b border-l border-default px-2 py-1 rounded-br-md rounded-bl-md bg-elevated flex items-center justify-between">
                                <p class="uppercase text-sm font-semibold">Subtotal</p>
                                <p class="font-semibold">{{ `₱ ${subtotal}` }}</p>
                            </div>
                        </div>
                    </template>
                </JobItemPricingBreakdown>
                <!-- Cancel / Save Buttons -->
                <div class="flex justify-end gap-4">
                    <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg" class="w-40"
                        @click="() => { isOpen = false }" />
                    <UButton label="Save Changes" icon="i-lucide-save" color="primary" size="lg"
                        class="w-40 font-semibold" type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>