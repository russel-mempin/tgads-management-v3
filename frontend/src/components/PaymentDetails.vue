<script setup lang="ts">
import type { PaymentForReview } from '@/types/forReview';
import { formatCurrency, formatDate } from '@/utils/formatters';

const props = defineProps<{
    entity: PaymentForReview['entity']
}>()
</script>

<template>
    <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
        <div class="flex items-center gap-3">
            <UIcon name="i-lucide-philippine-peso" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
            <h2 class="text-highlighted font-semibold">Payment Details</h2>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <div>
                <p class="text-sm uppercase text-muted">Amount</p>
                <p class="text-highlighted">{{ formatCurrency(props.entity.amount) }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Date received</p>
                <p class="text-highlighted">{{ formatDate(props.entity.date_received) }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Customer Name</p>
                <p class="text-highlighted">{{ props.entity.customer_name }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Method</p>
                <p class="text-highlighted">{{ props.entity.account_name }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Description</p>
                <p class="text-highlighted">{{ props.entity.description }}</p>
            </div>
        </div>
    </section>
</template>