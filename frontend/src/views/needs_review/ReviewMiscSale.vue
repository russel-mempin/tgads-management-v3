<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import type { MiscSaleForReview } from '@/types/forReview';
import { getMiscSaleDetails } from '@/api/forReviews';
import { formatCurrency, formatDate } from '@/utils/formatters';
import ReviewFields from '@/components/ReviewFields.vue';

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
        reviewData.value = await getMiscSaleDetails(forReviewId)
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    await fetchReviewDetails()
})

const daysSinceFlagging = computed(() => {
    if (!reviewData.value?.created_at) {
        return 0
    }

    const createdAt = new Date(reviewData.value.created_at)
    const now = new Date()

    const diffMs = now.getTime() - createdAt.getTime()
    return Math.floor(diffMs / (1000 * 60 * 60 * 24))
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
                <h2 class="text-xl text-highlighted font-semibold">Misc Sale</h2>
                <p>Reference No. {{ reviewData.entity_reference ? reviewData.entity_reference : 'N/A' }}</p>
            </div>
            <p>Edited by {{ reviewData.created_by_name }} {{ daysSinceFlagging }}d ago</p>
            <ReviewFields :old-data="reviewData.old_data" :new-data="reviewData.new_data" :entity="reviewData.entity" />
            <div class="grid grid-cols-2 gap-6">
                <UButton color="error" icon="i-lucide-x" label="Restore old data" class="flex w-full justify-center" />
                <UButton color="success" icon="i-lucide-check" label="Keep new data" class="flex w-full justify-center" />
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