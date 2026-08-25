<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

// Type imports
import type { PaymentForReview } from '@/types/forReview';
// Component imports
import { getPaymentForReviewDetails } from '@/api/forReviews';
import { formatCurrency, matchPercentage, formatJobItem, matchPercentageClass } from '@/utils/formatters';

const route = useRoute()
// Data variables
const reviewData = ref<PaymentForReview>()
const selectedMatchId = ref<string | null>(null)

// UI Variables
const loading = ref(true)
const resolutionType = ref<'job_order' | 'misc_sale'>('job_order')
const isSearchingManually = ref(false)

// Data functions
const fetchReviewDetails = async () => {
    loading.value = true
    try {
        const forReviewId = route.params.entity_id
        if (typeof forReviewId !== 'string') {
            throw new Error('Invalid entity id.')
        }
        reviewData.value = await getPaymentForReviewDetails(forReviewId)
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
                <h2 class="text-xl text-highlighted font-semibold">Review Payment</h2>
                <p>Reference No. {{ reviewData.entity_reference }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <PaymentDetails :entity="reviewData.entity" />
                <FlagDetails :flag-data="reviewData" />
            </div>
            <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
                <div class="flex items-center gap-3">
                    <UIcon name="i-lucide-square-check-big"
                        class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                    <h2 class="text-highlighted font-semibold">Resolve this payment</h2>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <UButton label="Link to Job Order" icon="i-lucide-briefcase" class="flex justify-center py-2"
                        :variant="resolutionType === 'job_order' ? 'solid' : 'outline'"
                        @click="resolutionType = 'job_order'" />

                    <UButton label="Mark as Misc Sale" icon="i-lucide-receipt-text" class="flex justify-center py-2"
                        :variant="resolutionType === 'misc_sale' ? 'solid' : 'outline'"
                        @click="resolutionType = 'misc_sale'" />
                </div>
                <div>
                    <div>
                        <div v-if="!isSearchingManually" class="flex items-center justify-between mb-4">
                            <p class="text-muted">Suggested matches, ranked by score</p>
                            <UButton label="Search manually" variant="outline" color="neutral" />
                        </div>
                        <UInput v-else="" icon="i-lucide-search" placeholder="Search job order number or customer name"
                            class="w-full mb-4" />
                    </div>
                    <div class="flex flex-col gap-2">
                        <div v-for="match in reviewData.entity.possible_matches" :key="match.id"
                            @click="selectedMatchId = match.id" :class="[
                                'rounded-sm border px-4 py-2 flex justify-between mb-2 cursor-pointer transition-colors',
                                selectedMatchId === match.id
                                    ? 'border-primary bg-primary/10'
                                    : 'border-default hover:bg-elevated'
                            ]">
                            <div class="flex flex-col justify-between">
                                <p class="font-semibold text-highlighted">{{ match.jo_number }}</p>
                                <p>{{ match.customer_name }}</p>

                                <div class="flex gap-2">
                                    <p v-for="item in match.job_items" :key="item.item_id">
                                        {{ formatJobItem(item) }}
                                    </p>
                                </div>
                            </div>

                            <div class="text-right">
                                <p class="font-semibold" :class="matchPercentageClass(match.match_score)">
                                    {{ matchPercentage(match.match_score) }}% match
                                </p>

                                <p>Balance: {{ formatCurrency(match.remaining_balance) }}</p>

                                <div class="mt-2 flex gap-2 justify-end">
                                    <p v-for="matchReason in match.match_reasons" :key="matchReason"
                                        class="w-fit uppercase text-xs font-semibold rounded-md px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300">
                                        {{ matchReason }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
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