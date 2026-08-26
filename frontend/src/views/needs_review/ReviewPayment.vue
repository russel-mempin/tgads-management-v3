<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
// Type imports
import type { PaymentForReview, PossibleMatch } from '@/types/forReview';
// API call imports
import { getPaymentForReviewDetails } from '@/api/forReviews';

const route = useRoute()
// Data variables
const reviewData = ref<PaymentForReview>()
const possibleJobOrders = ref<PossibleMatch[]>([])

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
        const data = await getPaymentForReviewDetails(forReviewId)
        reviewData.value = data
        possibleJobOrders.value = data.entity.possible_matches
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    await fetchReviewDetails()
})
</script>

<template>
    <Transition name="fade" mode="out-in">
        <div v-if="loading" class="flex items-center justify-center py-24">
            <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-muted" />
        </div>
        <div v-else-if="reviewData" class="m-6 flex flex-col gap-4">
            <!-- Back + Title -->
            <div class="flex items-center justify-between">
                <UButton icon="i-lucide-arrow-left" label="Back to Needs Review" color="neutral" variant="outline"
                    to="/review-data" />
            </div>
            <div>
                <h2 class="text-xl text-highlighted font-semibold">Review Payment</h2>
                <p>Reference No. {{ reviewData.entity_reference }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <PaymentDetails :entity="reviewData.entity" />
                <FlagDetails :flag-data="reviewData" />
            </div>
            <ResolvePaymentSection :initial-matches="reviewData.entity.possible_matches" :entity-id="reviewData.entity_id" />
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