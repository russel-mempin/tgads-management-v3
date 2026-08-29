<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// Type imports
import type { JobForReview } from '@/types/forReview';
import type { JobItemCreate, JobItem, JobItemTableRow } from '@/types/jobOrder';
import type { Service } from '@/types/service';
// API calls
import { getJobForReviewDetails } from '@/api/forReviews';
import { createJobItem } from '@/api/jobOrders';
import { getAllServices } from '@/api/services';
// Component imports
import FlagHeader from '@/components/FlagHeader.vue';
import JobOrderHeader from '@/components/JobOrderHeader.vue';
import OrderSummary from '@/components/OrderSummary.vue';
import PaymentTable from '@/components/PaymentTable.vue';

const route = useRoute()
const toast = useToast()
// Data variables
const reviewData = ref<JobForReview>()
const selectedJobItem = ref<JobItem | null>(null)
const serviceList = ref<Service[]>([])

// UI Variables
const loading = ref(true)
const isAddItemFormOpen = ref(false)

// Data functions
const fetchReviewDetails = async () => {
    loading.value = true
    try {
        const forReviewId = route.params.entity_id
        if (typeof forReviewId !== 'string') {
            throw new Error('Invalid entity id.')
        }
        reviewData.value = await getJobForReviewDetails(forReviewId)
    }
    finally {
        loading.value = false
    }
}
onMounted(async () => {
    fetchReviewDetails()
    serviceList.value = await getAllServices()
})

// UI functions
const openEditItemForm = (item: JobItemTableRow) => {
    const service = serviceList.value.find(
        service => service.name === item.service_name_snapshot
    )
    if (!item.id) {
        console.error(`Job item has no ID: ${item.item_id}`)
        return
    }
    if (!service?.id) {
        console.error(`Service not found: ${item.service_name_snapshot}`)
        return
    }
    const option = service.options.find(
        option => option.name === item.service_option_name_snapshot
    )
    if (!option?.id) {
        console.error(
            `Option not found: ${item.service_option_name_snapshot}`
        )
        return
    }
    selectedJobItem.value = {
        ...item,
        id: item.id,
        service_id: service.id,
        service_option_id: option.id,
        service_abbreviation_snapshot: service.abbreviation
    }
    isAddItemFormOpen.value = true
}
const openAddItemForm = () => {
    isAddItemFormOpen.value = true
}

// Data functions
const saveJobItem = async (item: JobItemCreate) => {
    if (!reviewData.value?.entity) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createJobItem(item, reviewData.value.entity_id)
        toast.add({
            title: 'Job Item Added.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchReviewDetails()
    }
    catch (error: unknown) {
        console.error('Failed to create payment:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to create payment.'
        }

        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
</script>

<template>
    <AddJobItemForm v-model:is-open="isAddItemFormOpen" :jo-number="reviewData?.entity.jo_number" :editing-item="selectedJobItem" @save="saveJobItem" />
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
            <FlagHeader :flag-data="reviewData" />
            <!-- <JobOrderHeader :entity-data="reviewData.entity" /> -->
            <OrderSummary :job-order="reviewData.entity" />
            <JobItemTable :job-items="reviewData.entity.job_items" :jo-number="reviewData.entity.jo_number">
                <template #header-actions>
                    <UTooltip :text="!reviewData.entity.jo_number ? 'A valid job order number is required' : 'Add an item'">
                        <span>
                            <UButton @click="openAddItemForm" :disabled="!reviewData.entity.jo_number || reviewData.entity.jo_number <= 0" icon="i-lucide-plus"
                                label="Add Item" variant="outline" />
                        </span>
                    </UTooltip>
                </template>
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
                </template>
            </JobItemTable>
            <PaymentTable :payments="reviewData.entity.payments" :balance="Number(reviewData?.entity.balance)" />
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