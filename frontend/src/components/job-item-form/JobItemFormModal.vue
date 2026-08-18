<script setup lang="ts">
import type { JobItemCreate } from '@/types/jobOrder.ts';
// Component imports
import JobItemServiceFields from './JobItemServiceFields.vue';
import JobItemWorkflowFields from './JobItemWorkflowFields.vue';
// import JobItemServiceFields from './JobItemServiceFields.vue';
import JobItemPricingBreakdown from './JobItemServiceFields.vue';

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

const handleSave = () => {
    console.log("Hi") 
    // emit('save', item)
}
</script>

<template>
    <UModal v-model:open="isOpen" @submit="handleSave">
        <template #body>
            <UForm>
                <!-- <JobItemServiceFields
                    :services="serviceList"
                    :is-area-based="isAreaBased"
                    v-model:service="state.selectedService"
                    v-model:option="state.selectedOption"
                    v-model:width="state.width"
                    v-model:height="state.height"
                    v-model:unit="state.unit"
                    v-model:quantity="state.quantity"
                />
                <JobItemWorkflowFields 
                    v-model:job-status="state.jobStatus"
                    v-model:due-date="state.dueDate"
                    v-model:description="state.description"
                    v-model:notes="state.notes"
                />
                <JobItemPricingBreakdown
                    :extra-list="extraList"
                    v-model:service-id="state.selectedService"
                    v-model:service-option-id="state.selectedOption"
                    v-model:width="state.width"
                    v-model:height="state.height"
                    v-model:unit="state.unit"
                    v-model:quantity="state.quantity"
                    v-model:extra-charge="state.extraCharge"
                    v-model:extras="state.extras"
                /> -->
                <!-- <div class="flex justify-end gap-4">
                    <UButton label="Cancel" @click="isOpen = false" />

                    <UButton label="Save" type="submit" />
                </div> -->
            </UForm>
        </template>
    </UModal>
</template>