<script setup lang="ts">
import { ref, onMounted, resolveComponent } from 'vue';
import { useRoute } from 'vue-router';
import { getServiceData } from '@/api/services';
import type { Service } from '@/types/service';
import { formatCurrency, formatDate } from '@/utils/formatters';

const route = useRoute()
const UBadge = resolveComponent('UBadge')

const serviceData = ref<Service>()

// UI Variables
const loading = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        const serviceId = route.params.service_id
        if (typeof serviceId !== 'string') {
            throw new Error('Invalid service ID')
        }
        serviceData.value = await getServiceData(serviceId)
        console.log(serviceData.value)
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
</script>
<template>
    <div class="m-4 pb-4 flex justify-between items-end border-b border-default">
        <div>
            <span class="flex items-end gap-2">
                <p class="font-bold text-3xl">{{ serviceData?.name }}</p>
                <p>{{ serviceData?.abbreviation }}</p>
            </span>
            <UBadge :color="serviceData?.is_active ? 'success' : 'error'">{{ serviceData?.is_active ? 'Active' :
                'Inactive' }}</UBadge>
        </div>
        <div class="text-right text-muted">
            <p> created {{ formatDate(serviceData?.created_at) }}</p>
            <p>last update {{ formatDate(serviceData?.updated_at) }}</p>
        </div>
    </div>
    <div class="m-4 p-4 grid grid-cols-3 gap-4 bg-default border border-default rounded-md divide-x divide-default">
        <div>
            <p class="uppercase text-sm font-semibold text-muted">Pricing Strategy</p>
            <p class="font-semibold">{{ serviceData?.pricing_strategy }}</p>
        </div>
        <div>
            <p class="uppercase text-sm font-semibold text-muted">Unit</p>
            <p class="font-semibold">{{ serviceData?.unit }}</p>
        </div>
        <div>
            <p class="uppercase text-sm font-semibold text-muted">Priced Options</p>
            <p class="font-semibold">Data</p>
        </div>
    </div>
    <div class="px-4">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options</p>
            <p class="text-muted">{{ serviceData?.options.length }} options</p>
        </span>
        <div class="flex flex-col gap-4">
            <div v-for="option in serviceData?.options" class="rounded-md border border-default">
                <div class="p-4 rounded-t-md bg-default border-b border-default flex items-center justify-between">
                    <span>
                        <p class="font-semibold">{{ option.name }}</p>
                        <p class="text-muted">{{ option.full_service_name }}</p>
                    </span>
                    <p class="text-lg font-semibold text-green-700">{{ formatCurrency(option.base_rate) }}</p>
                </div>
                <div v-if="option.price_tiers?.length">Pricing tiers</div>
                <p v-else class="p-4 text-sm text-muted">No tiered pricing - flat base rate applies at all quantities/consumption</p>
            </div>
        </div>
    </div>
</template>