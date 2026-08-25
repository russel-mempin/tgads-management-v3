<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
// Type imports
import type { PaymentForReview } from '@/types/forReview';
import type { MiscSaleCreate } from '@/types/miscSale';
// Component imports
import { getPaymentForReviewDetails } from '@/api/forReviews';
import MatchesList from '@/components/MatchesList.vue';
import MiscSaleForm from '@/components/MiscSaleForm.vue';
import { utcToInput } from '@/utils/formatters';

const route = useRoute()
// Data variables
const reviewData = ref<PaymentForReview>()
const selectedMatchId = ref<string | null>(null)
const miscSale = ref<MiscSaleCreate>({
    amount: 0,
    date: '',
    description: '',
})

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
        const data = await getPaymentForReviewDetails(forReviewId)
        reviewData.value = data
        console.log(data)
        miscSale.value = {
            amount: data.entity.amount,
            date: utcToInput(data.entity.date_received),
            description: data.entity.description ?? '',
        }
        console.log(miscSale.value)
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
            <!-- Resolve this payment -->
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
                <div class="border-b border-default pb-4">
                    <!-- Controls -->
                    <div v-if="resolutionType === 'job_order'">
                        <div v-if="!isSearchingManually" class="flex items-center justify-between mb-4">
                            <p class="text-muted">Suggested matches, ranked by score</p>
                            <UButton label="Search manually" variant="outline" color="neutral"
                                @click="() => { isSearchingManually = true }" />
                        </div>
                        <div v-else class="flex items-center gap-4 mb-4">
                            <UInput icon="i-lucide-search" placeholder="Search job order number or customer name"
                                class="w-full" />
                            <UButton label="Back to Suggestions" variant="outline" color="neutral"
                                @click="() => { isSearchingManually = false }" />
                        </div>
                    </div>
                    <!-- Form -->
                    <MatchesList v-if="resolutionType === 'job_order'"
                        :matches-list="reviewData.entity.possible_matches"
                        v-model:selected-match-id="selectedMatchId" />
                    <MiscSaleForm v-else-if="resolutionType === 'misc_sale'" v-model:amount="miscSale.amount"
                        v-model:date="miscSale.date" v-model:description="miscSale.description" />
                </div>
                <UFormField label="Resolution note" required>
                    <UTextarea class="w-full" />
                </UFormField>
                <UButton label="Confirm and mark as resolved" icon="i-lucide-check"
                    class="flex w-full justify-center" />
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