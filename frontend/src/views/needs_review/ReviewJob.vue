<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

// Type imports
import type { JobForReview } from '@/types/forReview';
import { getJobForReviewDetails } from '@/api/forReviews';
import FlagHeader from '@/components/FlagHeader.vue';

const route = useRoute()
// Data variables
const reviewData = ref<JobForReview>()

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
        reviewData.value = await getJobForReviewDetails(forReviewId)
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
        <div v-else-if="reviewData" class="m-6 flex flex-col gap-4">
            <!-- Back + Title -->
            <div class="flex items-center justify-between">
                <UButton icon="i-lucide-arrow-left" label="Back to Needs Review" color="neutral" variant="outline"
                    to="/review-data" />
            </div>
            <div>
                <h2 class="text-xl text-highlighted font-semibold">Review Job Order</h2>
                <p>Job Order No. {{ reviewData.entity_reference }}</p>
            </div>
            <FlagHeader />
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