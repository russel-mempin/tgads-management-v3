<script setup lang="ts">
import { getReviewCategoryColor, formatDate } from '@/utils/formatters';
import type { PaymentForReview } from '@/types/forReview';

const props = defineProps<{
    flagData: Pick<
        PaymentForReview,
        | 'reason_category'
        | 'created_at'
        | 'created_by_name'
        | 'reason'
        | 'resolved_at'
        | 'resolved_by_name'
    >
}>()
</script>

<template>
    <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
        <div class="flex items-center gap-3">
            <UIcon name="i-lucide-flag" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
            <h2 class="text-highlighted font-semibold">Flag Details</h2>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <div>
                <p class="text-sm uppercase text-muted">Reason Category</p>
                <UBadge :color="getReviewCategoryColor(props.flagData.reason_category)" variant="solid" size="lg">{{
                    props.flagData.reason_category }}</UBadge>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Flagged At</p>
                <p class="text-highlighted">{{ formatDate(props.flagData.created_at) }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Flagged By</p>
                <p class="text-highlighted">{{ props.flagData.created_by_name }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Reason</p>
                <p class="text-highlighted">{{ props.flagData.reason }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Resolved At</p>
                <p class="text-highlighted">{{ formatDate(props.flagData.resolved_at) ?? '-' }}</p>
            </div>
            <div>
                <p class="text-sm uppercase text-muted">Resolved By</p>
                <p class="text-highlighted">{{ props.flagData.resolved_by_name ?? '-' }}</p>
            </div>
        </div>
    </section>
</template>