<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

// Type imports
import type { PaymentForReview } from '@/types/forReview';
import { getPaymentForReviewDetails } from '@/api/forReviews';
// Component imports
import { getReviewCategoryColor, formatDate } from '@/utils/formatters';

const route = useRoute()
// Data variables
const reviewData = ref<PaymentForReview>()

// UI Variables
const loading = ref(true)

// Data functions
const fetchReviewDetails = async () => {
    loading.value = true
    try {
        const forReviewId = route.params.entity_id
        if (typeof forReviewId !== 'string') {
            throw new Error('Invalid entity id.')
        }
        reviewData.value = await getPaymentForReviewDetails(forReviewId)
        console.log(reviewData.value)
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    fetchReviewDetails()
})
</script>

<template>
    <Transition name="fade" mode="out-in">
        <div v-if="loading" class="flex items-center justify-center py-24">
            <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-muted" />
        </div>
        <div v-else-if="reviewData" class="m-6 flex flex-col gap-6">
            <!-- Back + Title -->
            <div class="flex items-center justify-between">
                <UButton icon="i-lucide-arrow-left" label="Back to Needs Review" color="neutral" variant="outline"
                    to="/review-data" />
            </div>
            <div>
                <h2 class="text-lg text-highlighted font-semibold">Review Payment</h2>
                <p># {{ reviewData.entity_reference }}</p>
            </div>
            <div class="grid grid-cols-2 gap-6">
                <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
                    <div class="flex items-center gap-3">
                        <UIcon name="i-lucide-philippine-peso"
                            class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                        <h2 class="text-highlighted font-semibold">Payment Details</h2>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm uppercase text-muted">Amount</p>
                            <p class="text-lg text-highlighted">{{ reviewData.entity.amount }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Date received</p>
                            <p class="text-lg text-highlighted">{{ formatDate(reviewData.entity.date_received) }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Customer Name</p>
                            <p class="text-lg text-highlighted">{{ reviewData.entity.customer_name }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Method</p>
                            <p class="text-lg text-highlighted">{{ reviewData.entity.account_name }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Description</p>
                            <p class="text-lg text-highlighted">{{ reviewData.entity.description }}</p>
                        </div>
                    </div>
                </section>
                <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
                    <div class="flex items-center gap-3">
                        <UIcon name="i-lucide-flag" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                        <h2 class="text-highlighted font-semibold">Flag Details</h2>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm uppercase text-muted">Reason Category</p>
                            <UBadge :color="getReviewCategoryColor(reviewData.reason_category)" variant="solid"
                                size="lg">{{
                                    reviewData.reason_category }}</UBadge>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Flagged At</p>
                            <p class="text-lg text-highlighted">{{ formatDate(reviewData.created_at) }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Flagged By</p>
                            <p class="text-lg text-highlighted">{{ reviewData.created_by_name }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Reason</p>
                            <p class="text-lg text-highlighted">{{ reviewData.reason }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Resolved At</p>
                            <p class="text-lg text-highlighted">{{ formatDate(reviewData.resolved_at) ?? '-' }}</p>
                        </div>
                        <div>
                            <p class="text-sm uppercase text-muted">Resolved By</p>
                            <p class="text-lg text-highlighted">{{ reviewData.resolved_by_name ?? '-' }}</p>
                        </div>
                    </div>
                </section>
            </div>
            <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
                <div class="flex items-center gap-3">
                    <UIcon name="i-lucide-square-check-big" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                    <h2 class="text-highlighted font-semibold">Resolve this payment</h2>
                </div>
                <div class="grid grid-cols-2 gap-4">
                </div>
            </section>
        </div>
    </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>