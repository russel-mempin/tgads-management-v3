<script setup lang="ts">
import { computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { ServiceSales } from '@/types/dashboard';
import type { ApexOptions } from 'apexcharts';

const props = defineProps<{
    data: ServiceSales[]
}>()

const series = computed(() => [
    {
        name: 'Sales',
        data: props.data.map(item => item.amount),
    },
])

const chartOptions = computed<ApexOptions>(() => ({
    chart: {
        type: 'bar',
        toolbar: { show: false },
    },
    plotOptions: {
        bar: {
            horizontal: true,
            distributed: true,
        },
    },
    xaxis: {
        categories: props.data.map(item => item.service_abbreviation),
    },
    dataLabels: {
        enabled: true,
        formatter: (value: number) => `₱${value.toLocaleString()}`,
    },
    tooltip: {
        y: {
            formatter: (value: number) => `₱${value.toLocaleString()}`,
        },
    },
    legend: { show: false },
}))
</script>

<template>
    <VueApexCharts
        type="bar"
        height="350"
        :options="chartOptions"
        :series="series"
    />
</template>