<script setup lang="ts">
// JobItemsForm.vue
import { Button, Dialog, InputText, Select, InputNumber, DatePicker } from 'primevue'
import { ref, onMounted, watch, computed } from 'vue'
import type { ServiceType } from '@/types/services'
import { computePrice } from '@/api/job_orders';
import { getAllServices, getAllExtras } from '@/api/services';
import type { JobItemCreate } from '@/types/job_orders';

const props = defineProps<{
    isVisible: boolean
    joNumber: number
    existingItems: JobItemCreate[]
    editItem?: JobItemCreate | null
}>()

const item = ref<JobItemCreate>({
    jo_number: '',
    item_id: '',
    description: '',
    height: 0,
    width: 0,
    size_unit: '',
    paper_size: '',
    quantity: 1,
    job_status: '',
    due_date: new Date(),
    discount: 0,
    service_type_id: '',
    extra_type_id: null,
    service_name: '',
    extra_service_name: '',
    extra_service_price: 0,
    unit_price: 0,
    notes: '',
})
const serviceList = ref<ServiceType[]>([]);
const extraList = ref<{ id: string, name: string, price: number }[]>([]);
const paperSizes = ref(['N/A', 'Short', 'Long', 'A4', 'A3'])
const jobStatuses = ref(['For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled'])
const previewItemId = computed(() => {
    if (!item.value.service_name) return 'Select a service type first'
    const abbreviation = serviceList.value.find(s => s.name === item.value.service_name)?.abbreviation ?? 'NULL'

    if (props.editItem) {
        return props.editItem.item_id
    }

    const count = props.existingItems.filter((i: JobItemCreate) => i.service_name === item.value.service_name).length + 1
    return `${props.joNumber}-${abbreviation}-${count}`
})

onMounted(async () => {
    serviceList.value = await getAllServices()
    extraList.value = await getAllExtras()
});

const onServiceChange = (service: ServiceType) => {
    item.value.service_type_id = service.id
    item.value.service_name = service.name
    item.value.size_unit = service.required_measurement_unit
}

const onExtraChange = (extra: { id: string, name: string, price: number }) => {
    item.value.extra_type_id = extra.id
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
            item.value.unit_price = await computePrice(height, width, service_name)
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
    (e: 'add-item', value: JobItemCreate): void
    (e: 'update-item', value: JobItemCreate): void
}>()

const resetItem = () => {
    item.value = {
        jo_number: '',
        item_id: '',
        description: '',
        height: 0,
        width: 0,
        size_unit: '',
        paper_size: '',
        quantity: 1,
        job_status: '',
        due_date: new Date(),
        discount: 0,
        service_type_id: '',
        extra_type_id: null,
        service_name: '',
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
            <label class="font-semibold mb-1">Item ID</label>
            <InputText :modelValue="previewItemId" fluid autocomplete="off" disabled />
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Service Type</label>
                <Select :modelValue="serviceList.find((s: ServiceType) => s.name === item.service_name)"
                    :options="serviceList" optionLabel="name" placeholder="Service Type"
                    @change="(e) => onServiceChange(e.value)" fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Extra Type</label>
                <Select
                    :modelValue="extraList.find((s: { name: string, price: number }) => s.name === item.extra_service_name)"
                    :options="extraList" optionLabel="name" placeholder="Extra Type"
                    @change="(e) => onExtraChange(e.value)" />
            </div>
        </div>
        <div class="grid grid-cols-3 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Height</label>
                <InputNumber v-model="item.height" fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Width</label>
                <InputNumber v-model="item.width" fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Unit Size</label>
                <InputText v-model="item.size_unit" fluid autocomplete="off" disabled />
            </div>
        </div>
        <div class="flex flex-col mb-4">
            <label class="font-semibold mb-1">Paper Size</label>
            <Select v-model="item.paper_size" :options="paperSizes" fluid />
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Quantity</label>
                <InputNumber v-model="item.quantity" :min=1 fluid />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Discount</label>
                <InputNumber v-model="item.discount" mode="currency" currency="PHP" fluid />
            </div>
        </div>
        <div class="grid grid-cols-3 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Unit Price</label>
                <InputNumber v-model="item.unit_price" mode="currency" currency="PHP" fluid disabled />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Extra Price</label>
                <InputNumber v-model="item.extra_service_price" mode="currency" currency="PHP" fluid disabled />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Subtotal</label>
                <InputNumber :modelValue="(item.unit_price + item.extra_service_price - item.discount) * item.quantity"
                    mode="currency" currency="PHP" fluid disabled />
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
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Job Status</label>
                <Select v-model="item.job_status" :options="jobStatuses" />
            </div>
            <div class="flex flex-col">
                <label class="font-semibold mb-1">Due Date</label>
                <DatePicker v-model="item.due_date" showTime hourFormat="12" />
            </div>
        </div>
        <div class="flex justify-end gap-2">
            <Button label="Cancel" severity="secondary" @click="emit('update:isVisible', false)" />
            <Button label="Save" @click="onSave" />
        </div>
    </Dialog>
</template>