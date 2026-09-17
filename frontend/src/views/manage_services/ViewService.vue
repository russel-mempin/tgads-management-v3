<script setup lang="ts">
import { ref, onMounted, resolveComponent, computed } from 'vue';
import { useRoute } from 'vue-router';
import { getServiceData } from '@/api/services';
import type { Service } from '@/types/service';
import ServiceHeader from '@/components/ServiceHeader.vue';
import OptionCard from '@/components/OptionCard.vue';

const route = useRoute()
const UButton = resolveComponent('UButton')

const serviceData = ref<Service>()

// UI Variables
const serviceId = route.params.service_id
const loading = ref(false)

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
</script>

<template>
    <section class="m-4">
        <ServiceHeader v-if="serviceData" :service-data="serviceData"/>
    </section>
    <!-- Options -->
    <section class="px-4 my-4">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" />
        </span>
        <div class="flex flex-col gap-4">
            <OptionCard v-for="option in serviceData?.options" :key="option.id" :option="option"
                :service-unit="serviceData?.unit" />
        </div>
    </section>
</template>