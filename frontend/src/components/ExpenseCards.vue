<script setup lang="ts">
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { ExpenseSummary } from '@/types/expense';

const props = defineProps<{
    period: string
    summary: ExpenseSummary
}>()
</script>

<template>
    <div class="bg-default border border-default rounded-md p-4">
        <p class="text-muted font-bold uppercase text-sm">Total Expenses - {{ props.period }}</p>
        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">{{
            formatCurrency(Number(props.summary.total)) }}</p>
    </div>
    <div class="bg-default border border-default rounded-md p-4">
        <p class="text-muted font-bold uppercase text-sm">Number of Expenses</p>
        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">{{ props.summary.count }}</p>
    </div>
    <div class="bg-default border border-default rounded-md p-4">
        <p class="text-muted font-bold uppercase text-sm">Largest Expense</p>
        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">{{
            formatCurrency(Number(props.summary.largest?.amount)) }}</p>
        <p class="text-sm">
            {{ `${props.summary.largest?.description} on ${formatDate(props.summary.largest?.date)} under
            ${props.summary.largest?.category}.` }}
        </p>
    </div>
</template>