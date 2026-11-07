<script setup lang="ts">
import { ref } from 'vue';  
import type { DATE_PERIODS } from '@/utils/constants';

// TODO: Monthly sales and expenses
// TODO: Change to perfomance report
// TODO: Yearly performance per month income expense side by side
// TODO: When clicked, show details
// Top customers, top products

// Filter Variables
const period = ref<DATE_PERIODS>('this_month')

// UI Variables
const periods: { label: string; value: DATE_PERIODS }[] = [
    { label: 'Today', value: 'today' },
    { label: 'This Week', value: 'this_week' },
    { label: 'This Month', value: 'this_month' },
    { label: 'Last Month', value: 'last_month' },
    { label: 'This Year', value: 'this_year' },
    { label: 'All Time', value: 'all' },
]
</script>

<template>
    <section class="shrink-0 mx-6 mt-6 flex gap-2">
        <UButton v-for="item in periods" :key="item.value" :label="item.label" class="rounded-full"
            :variant="period === item.value ? 'solid' : 'outline'" @click="() => { period = item.value }" />
    </section>
</template>