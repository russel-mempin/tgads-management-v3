<script setup lang="ts">
// JobItemsForm.vue
import { Button, Dialog, InputText, Select, InputNumber, DatePicker, InputGroup, InputGroupAddon } from 'primevue'
import { ref, onMounted, watch, computed } from 'vue'
import type { ServiceType } from '@/types/services'
import { computePrice } from '@/api/job_orders';
import { getAllServices, getAllExtras } from '@/api/services';
import type { JobItem } from '@/types/job_orders';
import { formatCurrency, nowInManila } from '@/utils/formatters';

const props = defineProps<{
    isVisible: boolean
    joNumber: number
    existingItems: JobItem[]
    editItem?: JobItem | null
}>()

const item = ref<JobItem>({
    jo_number: props.joNumber,
    item_id: '',
    description: '',
    height: 0,
    width: 0,
    size_unit: 'ft.',
    quantity: 1,
    job_status: 'For Layout',
    due_date: nowInManila(),
    discount: 0,
    extra_charge: 0,
    service_name: 'Tarpaulin Regular',
    extra_service_name: 'N/A',
    extra_service_price: 0,
    unit_price: 0,
    notes: '',
})
const serviceList = ref<ServiceType[]>([]);
const extraList = ref<{ id: string, name: string, price: number }[]>([]);
const jobStatuses = ref(['Pending', 'For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled'])
const unitSizes = ref(['ft.', 'in.', 'cm.', 'mm.', 'meter', 'N/A'])
const selectedIsAreaBased = ref(true);

const previewItemId = computed(() => {
    if (!item.value.service_name) return 'Select a service type first'
    const abbreviation = serviceList.value.find(s => s.name === item.value.service_name)?.abbreviation ?? 'NULL'

    if (props.editItem) {
        return props.editItem.item_id
    }

    const count = props.existingItems.filter((i: JobItem) => i.service_name === item.value.service_name).length + 1
    return `${props.joNumber}-${abbreviation}-${count}`
})

onMounted(async () => {
    serviceList.value = await getAllServices()
    extraList.value = await getAllExtras()
});

const onServiceChange = (service: ServiceType) => {
    console.log(service)
    item.value.service_name = service.name
    selectedIsAreaBased.value = service.is_area_based
}

const onExtraChange = (extra: { id: string, name: string, price: number }) => {
    item.value.extra_service_name = extra.name
    item.value.extra_service_price = extra.price
}

watch(
    () => ({
        height: item.value.height,
        width: item.value.width,
        service_name: item.value.service_name
    }),
    async ({ height, width, service_name }) => {
        if (height > 0 && width > 0 && service_name) {
            item.value.unit_price = await computePrice(height, width, service_name, item.value.size_unit)
        }
    }
)

watch(() => props.editItem, (newItem) => {
    if (newItem) {
        item.value = { ...newItem }
    } else {
        resetItem()
    }
})

const emit = defineEmits<{
    (e: 'update:isVisible', value: boolean): void
    (e: 'add-item', value: JobItem): void
    (e: 'update-item', value: JobItem): void
}>()

const resetItem = () => {
    item.value = {
        jo_number: props.joNumber,
        item_id: '',
        description: '',
        height: 0,
        width: 0,
        size_unit: 'ft.',
        quantity: 1,
        job_status: '',
        due_date: nowInManila(),
        discount: 0,
        extra_charge: 0,
        service_name: 'Tarpaulin Regular',
        extra_service_name: '',
        extra_service_price: 0,
        unit_price: 0,
        notes: ''
    }
}

const onSave = () => {
    if (props.editItem) {
        emit('update-item', { ...item.value })
    } else {
        item.value.item_id = previewItemId.value
        emit('add-item', { ...item.value })
    }
    emit('update:isVisible', false)
    resetItem()
}
</script>

<template>
    <Dialog :visible="isVisible" @update:visible="emit('update:isVisible', $event)" modal
        :header="editItem ? 'Edit Job Item' : 'Add Job Item'" :style="{ width: '40rem' }">
        <div class="flex flex-col mb-4">
            <div class="flex items-center gap-2 mb-1">
                <label class="font-semibold">Item ID</label>
                <span
                    class="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-500">Auto-generated</span>
            </div>
            <InputText :modelValue="previewItemId" fluid autocomplete="off" disabled />
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Service Type <span class="text-red-500">*</span></label>
                <Select :modelValue="serviceList.find((s: ServiceType) => s.name === item.service_name)"
                    :options="serviceList" optionLabel="name" placeholder="Service Type" filter
                    filterMatchMode="contains" @change="(e) => onServiceChange(e.value)" fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Extra Type <span class="text-red-500">*</span></label>
                <Select
                    :modelValue="extraList.find((s: { name: string, price: number }) => s.name === item.extra_service_name)"
                    :options="extraList" optionLabel="name" placeholder="Extra Type" filter filterMatchMode="contains"
                    fluid @change="(e) => onExtraChange(e.value)" />
            </div>
        </div>
        <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0"
            enter-to-class="opacity-100" leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="selectedIsAreaBased" class="flex flex-col mb-4">
                <label class="font-semibold mb-1">Dimensions <span class="text-red-500">*</span></label>
                <InputGroup>
                    <InputNumber v-model="item.height" placeholder="Height" fluid :maxFractionDigits="4" />
                    <InputGroupAddon>×</InputGroupAddon>
                    <InputNumber v-model="item.width" placeholder="Width" fluid :maxFractionDigits="4" />
                    <Select v-model="item.size_unit" :options="unitSizes"
                        :pt="{ root: { class: '!flex-none !w-24' } }" />
                </InputGroup>
            </div>
        </Transition>
        <div class="grid grid-cols-3 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Quantity <span class="text-red-500">*</span></label>
                <InputNumber v-model="item.quantity" :min=1 fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Discount</label>
                <InputNumber v-model="item.discount" mode="currency" currency="PHP" fluid :minFractionDigits="0"
                    :maxFractionDigits="2" />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Extra Charge</label>
                <InputNumber v-model="item.extra_charge" mode="currency" currency="PHP" fluid :minFractionDigits="0"
                    :maxFractionDigits="2" />
            </div>
        </div>
        <div class="flex justify-between bg-gray-100 p-2 rounded-md mb-4">
            <div class="flex gap-2">
                <p>Unit Price - </p>
                <p>{{ formatCurrency(item.unit_price) }}</p>
            </div>
            <div class="flex gap-2">
                <p>Extra Price - </p>
                <p>{{ formatCurrency(item.extra_service_price) }}</p>
            </div>
            <div class="flex gap-2">
                <p>Subtotal - </p>
                <p>{{ formatCurrency(((item.unit_price ?? 0) + (item.extra_service_price ?? 0) + item.extra_charge -
                    item.discount) * item.quantity) }}</p>
            </div>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Job Status</label>
                <Select v-model="item.job_status" :options="jobStatuses" />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Due Date <span class="text-red-500">*</span></label>
                <DatePicker v-model="item.due_date" showTime hourFormat="12" dateFormat="M dd, yy" />
            </div>
        </div>
        <div class="flex flex-col mb-4">
            <label class="font-semibold mb-1">Description</label>
            <InputText v-model="item.description" fluid autocomplete="off" />
        </div>
        <div class="flex flex-col mb-4">
            <label class="font-semibold mb-1">Notes</label>
            <InputText v-model="item.notes" fluid autocomplete="off" />
        </div>
        <div class="flex items-center justify-end gap-2">
            <Button class="w-24" label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
            <Button class="w-24" label="Add" @click="onSave" />
        </div>
    </Dialog>
</template>