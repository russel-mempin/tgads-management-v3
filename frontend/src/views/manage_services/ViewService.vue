<script setup lang="ts">
import { ref, onMounted, resolveComponent } from 'vue';
import { useRoute } from 'vue-router';
import { getServiceData } from '@/api/services';
import type { Service, ServiceOption } from '@/types/service';
import ServiceHeader from '@/components/ServiceHeader.vue';
import OptionCard from '@/components/OptionCard.vue';
import ServiceOptionForm from '@/components/service-option-form/ServiceOptionForm.vue';

const route = useRoute()
const UButton = resolveComponent('UButton')

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
const openEditOptionForm = (option: ServiceOption) => {
    selectedOption.value = option
    isServiceOptionFormOpen.value = true
}
const openDeleteOptionConfirm = (option: ServiceOption) => {
    selectedOption.value = option
}
</script>

<template>
    <ServiceOptionForm v-model:is-open="isServiceOptionFormOpen" :parent_service_id="serviceId" :editing-option="selectedOption"/>
    <section class="m-4">
        <ServiceHeader v-if="serviceData" :service-data="serviceData"/>
    </section>
    <!-- Options -->
    <section class="px-4 my-4">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" @click="() => isServiceOptionFormOpen = true" />
        </span>
        <div class="flex flex-col gap-4">
            <OptionCard v-for="option in serviceData?.options" :key="option.id" :option="option"
                :service-unit="serviceData?.unit" @edit-option="openEditOptionForm" @delete-option="openDeleteOptionConfirm"/>
        </div>
    </section>
</template>