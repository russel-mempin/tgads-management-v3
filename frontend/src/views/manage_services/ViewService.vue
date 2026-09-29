<script setup lang="ts">
// Dependency imports
import { ref, onMounted, resolveComponent, watch } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
// API call imports
import { getServiceData, createOption, updateOption, archiveOption, activateOption } from '@/api/services';
// Type imports
import type { Service, ServiceOption, ServiceOptionCreate, ServiceOptionUpdate } from '@/types/service';
// Component imports
import ServiceHeader from '@/components/ServiceHeader.vue';
import OptionCard from '@/components/OptionCard.vue';
import ServiceOptionForm from '@/components/service-option-form/ServiceOptionForm.vue';
import ConfirmActionModal from '@/components/ConfirmActionModal.vue';
import { useReferenceStore } from '@/stores/reference';

const route = useRoute()
const UButton = resolveComponent('UButton')
const toast = useToast()
const referenceStore = useReferenceStore()

// Data Variables
const serviceData = ref<Service>()
const selectedOption = ref<ServiceOption>()

// UI Variables
const serviceId = route.params.service_id as string
const loading = ref(false)
const isServiceOptionFormOpen = ref(false)
const isDeactivateOptionConfirmOpen = ref(false)
const isActivateOptionConfirmOpen = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        if (typeof serviceId !== 'string') {
            throw new Error('Invalid service ID')
        }
        serviceData.value = await getServiceData(serviceId)
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
watch(isServiceOptionFormOpen, (isOpen) => {
    if (!isOpen) {
        selectedOption.value = undefined
    }
})
const saveOptionToDb = async (option: ServiceOptionCreate) => {
    try {
        await createOption(serviceId, option)
        toast.add({
            title: 'Service Option Added.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
    }
    catch (error: unknown) {
        console.error("Failed to create option:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to create payment.'
        }
        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const openEditOptionForm = (option: ServiceOption) => {
    selectedOption.value = option
    isServiceOptionFormOpen.value = true
}
const saveEditOptionToDb = async (option_id: string, option: ServiceOptionUpdate) => {
    try {
        await updateOption(serviceId, option_id, option)
        toast.add({
            title: 'Service Option Updated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
    }
    catch (error: unknown) {
        console.error("Failed to update option:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to update option.'
        }
        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}

const openDeleteOptionConfirm = (option: ServiceOption) => {
    selectedOption.value = option
    isDeactivateOptionConfirmOpen.value = true
}
const deactivateSelectedOption = async () => {
    loading.value = true
    try {
        await archiveOption(serviceId, selectedOption.value!.id)
        toast.add({
            title: 'Service Option Deactivated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
        isDeactivateOptionConfirmOpen.value = false
    }
    catch (error: unknown) {
        console.error("Failed to deactivate option:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to deactivate option.'
        }
        toast.add({
            title: 'Deactivating option failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
    finally {
        loading.value = false
    }
}

const openActivateOptionConfirm = (option: ServiceOption) => {
    selectedOption.value = option
    isActivateOptionConfirmOpen.value = true
}
const activateSelectedOption = async () => {
    try {
        await activateOption(serviceId, selectedOption.value!.id)
        toast.add({
            title: 'Service Option Activated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
        isActivateOptionConfirmOpen.value = false
    }
    catch (error: unknown) {
        console.error("Failed to activate option:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to activate option.'
        }
        toast.add({
            title: 'Activating option failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
    finally {
        loading.value = false
    }
}
</script>

<template>
    <ServiceOptionForm v-model:is-open="isServiceOptionFormOpen" @save="saveOptionToDb" @update="saveEditOptionToDb"
        :parent_service_id="serviceId" :editing-option="selectedOption" />
    <ConfirmActionModal
        v-model:is-open="isDeactivateOptionConfirmOpen"
        title="Deactivate Option"
        :description="`Are you sure you want to deactivate ${selectedOption?.full_service_name}?`"
        confirm-label="Yes, deactivate"
        confirm-icon="i-lucide-layers-arrow-down"
        confirm-color="warning"
        icon="i-lucide-layers-arrow-down"
        icon-color="text-warning"
        icon-background="bg-warning/10"
        @confirm="deactivateSelectedOption"
    />
    <ConfirmActionModal
        v-model:is-open="isActivateOptionConfirmOpen"
        title="Activate Option"
        :description="`Are you sure you want to activate ${selectedOption?.full_service_name}?`"
        confirm-label="Yes, activate"
        confirm-icon="i-lucide-layers-arrow-up"
        confirm-color="success"
        icon="i-lucide-layers-arrow-up"
        icon-color="text-success"
        icon-background="bg-success/10"
        @confirm="activateSelectedOption"
    />
    <section class="m-6">
        <ServiceHeader v-if="serviceData" :service-data="serviceData" />
    </section>
    <!-- Options -->
    <section class="px-6 my-6">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" @click="() => isServiceOptionFormOpen = true" />
        </span>
        <div class="flex flex-col gap-6">
            <OptionCard v-for="option in serviceData?.options" :key="option.id" :option="option"
                :service-unit="serviceData?.unit" @edit-option="openEditOptionForm"
                @delete-option="openDeleteOptionConfirm" @activate-option="openActivateOptionConfirm" />
        </div>
    </section>
</template>