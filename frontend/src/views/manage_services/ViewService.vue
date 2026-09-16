<script setup lang="ts">
import { ref, onMounted, resolveComponent } from 'vue';
import { useRoute } from 'vue-router';
import { getServiceData } from '@/api/services';
import type { Service } from '@/types/service';
import { formatCurrency } from '@/utils/formatters';

const route = useRoute()
const UButton = resolveComponent('UButton')

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
    <div class="m-4 pb-4 flex justify-between items-center border-b border-default">
        <span class="flex items-center gap-2">
            <p class="font-bold text-3xl">{{ serviceData?.name }}</p>
            <p>[{{ serviceData?.abbreviation }}]</p>
            <span :class="[
                'flex items-center gap-1.5 font-medium',
                serviceData?.is_active ? 'text-green-700' : 'text-red-700'
            ]">
                <span :class="[
                    'size-2 rounded-full',
                    serviceData?.is_active ? 'bg-green-700' : 'bg-red-700'
                ]" />
                {{ serviceData?.is_active ? 'Active' : 'Inactive' }}
            </span>
        </span>
        <UButton label="Edit Base Service" icon="i-lucide-pen-square" />
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
    <div class="px-4 my-4">
        <span class="flex justify-between items-center mb-4">
            <p class="text-xl font-semibold">Options ({{ serviceData?.options.length }})</p>
            <UButton label="Add Option" icon="i-lucide-plus" />
        </span>
        <div class="flex flex-col gap-4">
            <div v-for="option in serviceData?.options" class="rounded-md border border-default bg-default">
                <div class="p-4 border-b border-default flex items-center justify-between">
                    <div>
                        <span class="flex items-center gap-2">
                            <p class="font-semibold">{{ option.name }}</p>
                            <span :class="[
                                'flex items-center gap-1.5 font-medium',
                                option.is_active ? 'text-green-700' : 'text-red-700'
                            ]">
                                <span :class="[
                                    'size-2 rounded-full',
                                    option.is_active ? 'bg-green-700' : 'bg-red-700'
                                ]" />
                                {{ option.is_active ? 'Active' : 'Inactive' }}
                            </span>
                        </span>
                        <p class="text-muted text-sm">{{ option.full_service_name }}</p>
                    </div>

                    <p class="text-lg font-semibold text-green-700">{{ formatCurrency(option.base_rate) }}</p>
                </div>
                <div v-if="option.price_tiers?.length">
                    <div class="grid grid-cols-3 text-sm font-semibold text-muted bg-muted px-4 py-2 border-b border-default">
                        <p>Consumption ({{ serviceData?.unit }})</p>
                        <p>Rate</p>
                    </div>
                    <div v-for="price_tier in option.price_tiers"
                        class="grid grid-cols-3 p-4 border-default border-b last:border-b-0">
                        <p>{{ price_tier.min_threshold }} {{ price_tier.max_threshold ? `- ${price_tier.max_threshold}` : 'UP' }}</p>
                        <p>{{ formatCurrency(price_tier.rate) }}</p>
                        <UButton label="Edit" icon="i-lucide-pen-square"/>
                    </div>
                </div>
                <div v-else class="p-4 flex items-center justify-between">
                    <p class="text-sm text-muted">No tiered pricing - flat base rate applies
                        at all quantities/consumption</p>
                    <UButton label="Add Pricing Tier" icon="i-lucide-plus" variant="ghost" />
                </div>
            </div>
        </div>
    </div>
</template>