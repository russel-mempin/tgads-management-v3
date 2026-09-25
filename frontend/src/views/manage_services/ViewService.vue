<script setup lang="ts">
import { ref, onMounted, resolveComponent } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import { getServiceData, createOption } from '@/api/services';
import type { Service, ServiceOption, ServiceOptionCreate, ServiceOptionUpdate } from '@/types/service';
import ServiceHeader from '@/components/ServiceHeader.vue';
import OptionCard from '@/components/OptionCard.vue';
import ServiceOptionForm from '@/components/service-option-form/ServiceOptionForm.vue';

const route = useRoute()
const UButton = resolveComponent('UButton')
const toast = useToast()

// Data Variables
const serviceData = ref<Service>()
const selectedOption = ref<ServiceOption>()

// UI Variables
const serviceId = route.params.service_id as string
const loading = ref(false)
const isServiceOptionFormOpen = ref(false)

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
const saveOptionToDb = async(option: ServiceOptionCreate) => {
    try {
        await createOption(serviceId, option)
        toast.add({
            title: 'Service Option Added.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
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
const saveEditOptionToDb = async(option: ServiceOptionUpdate) => {
    console.log(option)
}
const openDeleteOptionConfirm = (option: ServiceOption) => {
    selectedOption.value = option
}
</script>

<template>
    <ServiceOptionForm v-model:is-open="isServiceOptionFormOpen" @save="saveOptionToDb" @update="saveEditOptionToDb" :parent_service_id="serviceId" :editing-option="selectedOption"/>
    <section class="m-6">
        <ServiceHeader v-if="serviceData" :service-data="serviceData"/>
    </section>
    <!-- Options -->
    <section class="px-6 my-6">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" @click="() => isServiceOptionFormOpen = true" />
        </span>
        <div class="flex flex-col gap-6">
            <OptionCard v-for="option in serviceData?.options" :key="option.id" :option="option"
                :service-unit="serviceData?.unit" @edit-option="openEditOptionForm" @delete-option="openDeleteOptionConfirm"/>
        </div>
    </section>
</template>