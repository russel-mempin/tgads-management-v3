<script setup lang="ts">
import { reactive, watch, ref, computed, onMounted } from 'vue';
import type { JobItem, PricingData } from '@/types/jobOrder';
import { z } from 'zod'
import type { Extra } from '@/types/service'
import { getUnitPrice, updateJobItem } from '@/api/jobOrders';
import { getAllExtras } from '@/api/services';
import type { FormSubmitEvent } from '@nuxt/ui';
import isEqual from 'lodash/isEqual'

const toast = useToast()

const emit = defineEmits<{
    updated: []
}>()

const props = defineProps<{
    jobItem?: JobItem | null
}>()
const isOpen = defineModel<boolean>('isOpen', { required: true })

// Form schemas
interface ExtraLineItem {
    extraId: string
    quantity: number
}
const extraSchema = z.object({
    extraId: z.string().min(1, 'Select an extra'),
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

// UI Variables
const statusOptions = ["Pending", "For Layout", "For Approval", "For Printing", "For Pickup", "Released", "Cancelled"]
const extraList = ref<Extra[]>([])
let debounceTimer: ReturnType<typeof setTimeout>
const extraChargeTotal = computed(() =>
    form.extra_charge * form.quantity
)
const getExtraPrice = (extra: ExtraLineItem) => {
    const extraData = extraList.value.find(x => x.id === extra.extraId)
    if (!extraData) return 0
    return extraData.price * extra.quantity
}
const extraTotal = computed(() =>
    form.extras.reduce((sum, e) => sum + getExtraPrice(e), 0)
)
const subtotal = computed(() =>
    ((pricingData.value?.unit_price ?? 0) * form.quantity) + extraTotal.value + extraChargeTotal.value - form.discount_amount
)
const isSubmitting = ref(false)

// Data variables
const pricingData = ref<PricingData>()

// Data functions
onMounted(async () => {
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
            extraId: extra.extra_service_id,
            quantity: extra.quantity,
        }))
    },
    { immediate: true }
)
// Get pricing as soon as opened
watch(
    () => [props.jobItem?.width, props.jobItem?.height, props.jobItem?.quantity, props.jobItem?.service_id, props.jobItem?.service_option_id, props.jobItem?.size_unit],
    () => {
        clearTimeout(debounceTimer)
        debounceTimer = setTimeout(async () => {
            if (!props.jobItem?.service_id || !props.jobItem.service_option_id || !props.jobItem?.quantity) return

            pricingData.value = await getUnitPrice({
                height: props.jobItem.height ?? 0,
                width: props.jobItem.width ?? 0,
                service_id: props.jobItem.service_id,
                option_id: props.jobItem.service_option_id,
                size_unit: props.jobItem.size_unit,
                quantity: props.jobItem.quantity
            })
        }, 400)
    },
    { immediate: true }
)

const getChanges = (): Record<string, unknown> => {
    if (!props.jobItem) return {}

    const changes: Record<string, unknown> = {}

    for (const key of Object.keys(form) as (keyof typeof form)[]) {
        const current = key === 'extras'
            ? form.extras.map(e => ({ extra_service_id: e.extraId, quantity: e.quantity }))
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

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
    if (isSubmitting.value) return

    isSubmitting.value = true

    try {
        if (props.jobItem) {
            // Editing an existing item — send only the diff
            const changes = getChanges()
            if (Object.keys(changes).length === 0) {
                // nothing changed, no need to hit the backend
                return
            }
            await updateJobItem(changes, props.jobItem.id)
            emit("updated")
            isOpen.value = false
        }
    }
    catch (error) {
        console.error('Failed to update job item:', error)
        toast.add({
            title: 'Save failed',
            description: 'Something went wrong while saving the job item.',
            color: 'error',
        })
    }
    finally {
        isSubmitting.value = false
    }
}

// UI Functions
const addExtra = () => {
    form.extras.push({ extraId: '', quantity: 1 })
}
const removeExtra = (index: number) => {
    form.extras.splice(index, 1)
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
                <div class="border border-default bg-muted rounded-md">
                    <div class="flex items-center justify-between p-4">
                        <p class="uppercase font-bold">Extras</p>
                        <UButton label="Add Extra" variant="subtle" icon="i-lucide-plus" @click="addExtra" />
                    </div>
                    <div v-if="!form.extras.length" class="p-4 text-sm text-muted text-center">
                        No extras added.
                    </div>
                    <div v-for="(extra, index) in form.extras" :key="index"
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
                        <UButton icon="i-lucide-trash-2" color="error" variant="ghost" @click="removeExtra(index)" />
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <UFormField label="Extra Charge (Per Piece)" name="extra_charge" class="w-full">
                        <UInputNumber v-model="form.extra_charge" :increment="false" :decrement="false"
                            :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                            class="w-full" :step="0.1" :step-snapping="false"
                            @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                    <UFormField label="Discount (Flat)" name="discount_amount" class="w-full">
                        <UInputNumber v-model="form.discount_amount" :increment="false" :decrement="false"
                            :format-options="{ style: 'currency', currency: 'PHP', currencyDisplay: 'code', currencySign: 'accounting' }"
                            class="w-full" :step="0.1" :step-snapping="false"
                            @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
                    </UFormField>
                </div>
                <!-- Pricing Breakdown -->
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
                <!-- Cancel / Save Buttons -->
                <div class="flex justify-end gap-4">
                    <UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg" class="w-40"
                        @click="() => { isOpen = false }" />
                    <UButton label="Save Changes    " icon="i-lucide-save" color="primary" size="lg"
                        class="w-40 font-semibold" type="submit" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>