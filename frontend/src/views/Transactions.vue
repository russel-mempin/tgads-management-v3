<script setup lang="ts">
import { ref } from 'vue';
import type { ExpensePeriod } from '@/types/expense';

const period = ref<ExpensePeriod>('this_month')

// UI Variables
const periods: { label: string; value: ExpensePeriod }[] = [
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
            :variant="period === item.value ? 'solid' : 'outline'" @click="period = item.value" />
    </section>
</template>