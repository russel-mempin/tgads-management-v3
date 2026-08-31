<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios'
// Type imports
import type { PaymentForReview } from '@/types/forReview';
import type { MiscSaleCreate } from '@/types/miscSale';
// API call imports
import { getPaymentForReviewDetails, assignPaymentDataToJob, assignPaymentDataToMisc } from '@/api/forReviews';

const route = useRoute()
const router = useRouter()
const toast = useToast()
// Data variables
const reviewData = ref<PaymentForReview | null>(null)

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
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    await fetchReviewDetails()
})

type Resolution =
    | {
        type: 'job_order'
        match: string
    }
    | {
        type: 'misc_sale'
        sale: MiscSaleCreate
    }
const saveToDb = async (resolution: Resolution) => {
    if (!reviewData.value?.entity) return
    if (resolution.type === 'job_order') {
        try {
            const res = await assignPaymentDataToJob(reviewData.value.entity_id, resolution.match)
            toast.add({
                title: res.message,
                color: 'success',
                icon: 'i-lucide-circle-check'
            })
            await router.push('/review-data')
        }
        catch (error) {
            if (axios.isAxiosError(error)) {
                console.log(error.response?.data)
            }
        }
    } 
    else if (resolution.type === 'misc_sale') {
        try {
            const res = await assignPaymentDataToMisc(reviewData.value.entity_id)
            toast.add({
                title: res.message,
                color: 'success',
                icon: 'i-lucide-circle-check'
            })
            await router.push('/review-data')
        }
        catch (error) {
            if (axios.isAxiosError(error)) {
                console.log(error.response?.data)
            }
        }
    }
}
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
            <ResolvePaymentSection :initial-matches="reviewData.entity.possible_matches" :entity="reviewData.entity"
                @resolve="saveToDb" />
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