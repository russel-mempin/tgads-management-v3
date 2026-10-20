```vue
<script setup lang="ts">
import { computed } from 'vue';
import type { ServiceSales } from '@/types/dashboard';
import { formatCurrency } from '@/utils/formatters';

const props = defineProps<{
    data: ServiceSales[]
}>()

const maxAmount = computed(() =>
    Math.max(...props.data.map(item => Number(item.amount)), 1)
)

const colors = [
    'bg-blue-500',
    'bg-violet-500',
    'bg-emerald-500',
    'bg-amber-500',
    'bg-rose-500',
    'bg-cyan-500',
]
</script>

<template>
    <div v-if="data.length" class="m-6 space-y-4">
        <div
            v-for="(item, index) in data"
            :key="item.service_abbreviation"
            class="grid grid-cols-[100px_minmax(0,1fr)_110px] items-center gap-3"
        >
            <span class="truncate">
                {{ item.service_abbreviation }}
            </span>

            <div class="h-7 overflow-hidden rounded-md bg-gray-100 dark:bg-gray-800">
                <div
                    class="h-full rounded-md transition-all duration-300"
                    :class="colors[index % colors.length]"
                    :style="{
                        width: `${Math.max(0, Number(item.amount)) / maxAmount * 100}%`
                    }"
                />
            </div>

            <span class="text-right font-semibold tabular-nums">
                {{ formatCurrency(Number(item.amount)) }}
            </span>
        </div>
    </div>
</template>
```