<script setup lang="ts">
// Dependency imports
import { ref, onMounted, resolveComponent, watch } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
// API call imports
import { getServiceData, createOption, updateOption, archiveOption, activateOption, updateService, deactivateService, reactivateService } from '@/api/services';
// Type imports
import type { Service, ServiceOption, ServiceOptionCreate, ServiceOptionUpdate } from '@/types/service';
// Component imports
import ServiceHeader from '@/components/ServiceHeader.vue';
import OptionCard from '@/components/OptionCard.vue';
import ServiceOptionForm from '@/components/service-option-form/ServiceOptionForm.vue';
import ConfirmActionModal from '@/components/ConfirmActionModal.vue';
import EditServiceForm from '@/components/EditServiceForm.vue';
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
const isEditServiceFormOpen = ref(false)
const isDeactivateServiceConfirmOpen = ref(false)

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
// Add Option
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
// Edit Option
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
// Deactivate Option
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
// Reactivate Option
const activateSelectedOption = async (option: ServiceOption) => {
    try {
        await activateOption(serviceId, option.id)
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
// Edit Service
const openEditServiceForm = () => {
    isEditServiceFormOpen.value = true
}
const saveEditServiceToDb = async (service: ServiceOptionUpdate) => {
    loading.value = true
    try {
        await updateService(serviceId, service)
        toast.add({
            title: 'Service Updated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
        isEditServiceFormOpen.value = false
    }
    catch (error: unknown) {
        console.error("Failed to update service:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to update service.'
        }
        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
    finally {
        loading.value = false
    }
}
// Deactivate Service
const deactivateServiceInDb = async () => {
    loading.value = true
    try {
        await deactivateService(serviceId)
        toast.add({
            title: 'Service deactivated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
        isDeactivateServiceConfirmOpen.value = false
    }
    catch (error: unknown) {
        console.error("Failed to deactivate service:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to deactivate service.'
        }
        toast.add({
            title: 'Saving changes failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
    finally {
        loading.value = false
    }
}
// Reactivate Service
const reactivateServiceInDb = async () => {
    loading.value = true
    try {
        await reactivateService(serviceId)
        toast.add({
            title: 'Service reactivated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
        isDeactivateServiceConfirmOpen.value = false
    }
    catch (error: unknown) {
        console.error("Failed to reactivate service:", error)
        let message = "An unexpected error occured."
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to reactivate service.'
        }
        toast.add({
            title: 'Saving changes failed.',
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
    <EditServiceForm v-model:is-open="isEditServiceFormOpen" :service-data="serviceData" @save="saveEditServiceToDb" />
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
        v-model:is-open="isDeactivateServiceConfirmOpen"
        title="Deactivate Service"
        :description="`Are you sure you want to deactivate the whole service? This will also deactivate the options related to it.`"
        confirm-label="Yes, deactivate"
        confirm-icon="i-lucide-layers-arrow-down"
        confirm-color="warning"
        icon="i-lucide-layers-arrow-down"
        icon-color="text-warning"
        icon-background="bg-warning/10"
        @confirm="deactivateServiceInDb"
    />
    <section class="m-6">
        <ServiceHeader v-if="serviceData" 
            :service-data="serviceData" 
            @edit-service="openEditServiceForm" 
            @deactivate-service="() => isDeactivateServiceConfirmOpen = true"
            @reactivate-service="reactivateServiceInDb"
        />
    </section>
    <!-- Options -->
    <section class="px-6 my-6">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" @click="() => isServiceOptionFormOpen = true" />
        </span>
        <div class="grid grid-cols-3 gap-6">
            <OptionCard v-for="option in serviceData?.options" :key="option.id" :option="option"
                :service-unit="serviceData?.unit" @edit-option="openEditOptionForm"
                @delete-option="openDeleteOptionConfirm" @activate-option="activateSelectedOption" />
        </div>
    </section>
</template>