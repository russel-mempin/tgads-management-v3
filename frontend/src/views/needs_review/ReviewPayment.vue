<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

// Type imports
import type { ForReviewDetails } from '@/types/forReview';
import { getPaymentForReviewDetails } from '@/api/forReviews';

const route = useRoute()
// Data variables
const reviewData = ref<ForReviewDetails>()

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
                <UButton icon="i-lucide-square-check-big" label="Mark as Resolved" color="success" variant="subtle" />
            </div>
            <div>
                <p class="text-2xl font-semibold text-highlighted">{{ `${reviewData.entity_type} · Reference Number #${reviewData.entity_reference}` }}</p>
                <UBadge />
            </div>
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