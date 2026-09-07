<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import type { MiscSaleForReview } from '@/types/forReview';
import { getMiscSaleDetails } from '@/api/forReviews';

const route = useRoute()

// Data variables
const reviewData = ref<MiscSaleForReview | null>(null)
// UI variables
const loading = ref(false)

// Data functions
const fetchReviewDetails = async () => {
    loading.value = true
    try {
        const forReviewId = route.params.misc_sale_id
        console.log(forReviewId)
        if (typeof forReviewId !== 'string') {
            throw new Error('Invalid entity id.')
        }
        const data = await getMiscSaleDetails(forReviewId)
        console.log(data)
        reviewData.value = data
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