<script setup lang="ts">
import { computed } from 'vue';
import type { Service } from '@/types/service';

const props = defineProps<{
    serviceData: Service
}>()

const pricedOptionCount = computed(() =>
    props.serviceData.options.filter(option => option.is_priced).length ?? 0
)
</script>

<template>
    <div class="flex justify-between items-center pb-4">
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
    <div class="p-4 grid grid-cols-3 gap-4 bg-default border border-default rounded-md divide-x divide-default">
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
            <p class="font-semibold">{{pricedOptionCount}} / {{ serviceData.options.length }}</p>
        </div>
    </div>
</template>