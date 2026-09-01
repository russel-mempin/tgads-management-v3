<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

// Type imports
import type { JobForReview } from '@/types/forReview';
import type { JobItemCreate, JobItem, JobItemTableRow, Payment } from '@/types/jobOrder';
import type { Service } from '@/types/service';
// API calls
import { getJobForReviewDetails, updateWholeJobItem, voidJobOrderAndDeleteReview, getJobItemWithJobOrder, markJobOrderAsResolved } from '@/api/forReviews';
import { createJobItem, createPayment } from '@/api/jobOrders';
import { getAllServices } from '@/api/services';
// Component imports
import FlagHeader from '@/components/FlagHeader.vue';
import OrderSummary from '@/components/OrderSummary.vue';
import PaymentTable from '@/components/PaymentTable.vue';
import PaymentForm from '@/components/PaymentForm.vue';

const route = useRoute()
const toast = useToast()
const router = useRouter()
// Data variables
const reviewData = ref<JobForReview>()
const selectedJobItem = ref<JobItem | null>(null)
const serviceList = ref<Service[]>([])
const voidReason = ref('')

// UI Variables
const loading = ref(true)
const isAddItemFormOpen = ref(false)
const isAddPaymentFormOpen = ref(false)
const isVoidConfirmOpen = ref(false)
const highlightedItemId = ref('')

// Data functions
const fetchReviewDetails = async () => {
    loading.value = true
    try {
        const entityId = route.params.entity_id
        if (typeof entityId !== 'string') {
            throw new Error('Invalid entity id.')
        }
        if (route.name === 'review-job-order') {
            reviewData.value = await getJobForReviewDetails(entityId)
        } else if (route.name === 'review-job-item') {
            reviewData.value = await getJobItemWithJobOrder(entityId)
            highlightedItemId.value = entityId
        } else {
            throw new Error('Invalid review route.')
        }
    } finally {
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

// Data functions
const saveJobItem = async (item: JobItemCreate) => {
    if (!reviewData.value?.entity) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    if (selectedJobItem.value) {
        try {
            await updateWholeJobItem(reviewData.value.entity_id, selectedJobItem.value.id, item)
            toast.add({
                title: 'Job Item Updated.',
                color: 'success',
                icon: 'i-lucide-circle-check'
            })
            await fetchReviewDetails()
        }
        catch (error: unknown) {
            console.error('Failed to save job item:', error)

            let message = 'An unexpected error occurred.'

            if (axios.isAxiosError(error)) {
                message = error.response?.data?.detail ?? 'Failed to save job item.'
            }

            toast.add({
                title: 'Saving data failed.',
                description: message,
                color: 'error',
                icon: 'i-lucide-x'
            })
        }
    }
    else if (!selectedJobItem.value) {
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
            console.error('Failed to save job item:', error)

            let message = 'An unexpected error occurred.'

            if (axios.isAxiosError(error)) {
                message = error.response?.data?.detail ?? 'Failed to save job item.'
            }

            toast.add({
                title: 'Saving data failed.',
                description: message,
                color: 'error',
                icon: 'i-lucide-x'
            })
        }
    }
}
const savePayment = async (item: Payment) => {
    if (!reviewData.value?.entity) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await createPayment(item, reviewData.value?.entity_id)
        toast.add({
            title: 'Payment data saved.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchReviewDetails()
    }
    catch (error: unknown) {
        console.error('Failed to save job item:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to save job item.'
        }

        toast.add({
            title: 'Saving data failed.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const voidJob = async () => {
    if (!reviewData.value?.entity) {
        console.error('Cannot save job item: Job order not loaded.')
        return
    }
    try {
        await voidJobOrderAndDeleteReview(voidReason.value, reviewData.value?.entity_id)
        toast.add({
            title: 'Job order voided.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await router.push('/review-data')
    }
    catch (error: unknown) {
        console.error('Failed to void job order:', error)

        let message = 'An unexpected error occurred.'

        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to save job item.'
        }

        toast.add({
            title: 'Failed to void job order.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
const confirmResolution = async () => {
    if (!reviewData.value?.entity) {
        console.error('Cannot resolve job order: Job order not loaded.')
        return
    }
    try {
        if (reviewData.value.entity_type === "Job Order") {
            console.log("Job Order")
            console.log(reviewData.value?.entity_id)
            await markJobOrderAsResolved(reviewData.value?.entity_id)
        }
        else if (reviewData.value.entity_type === "Job Item") {
            console.log("Job Item")
            console.log(reviewData.value?.entity.id)
            await markJobOrderAsResolved(reviewData.value?.entity.id)
        }
        toast.add({
            title: 'Job order marked as resolved.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await router.push('/review-data')
    }
    catch (error: unknown) {
        console.error('Failed to resolve job order:', error)
        let message = 'An unexpected error occurred.'
        if (axios.isAxiosError(error)) {
            message = error.response?.data?.detail ?? 'Failed to resolve job order.'
        }
        toast.add({
            title: 'Failed to resolve job order.',
            description: message,
            color: 'error',
            icon: 'i-lucide-x'
        })
    }
}
</script>

<template>
    <UModal title="Void Job Order" v-model:open="isVoidConfirmOpen">
        <template #body>
            <div class="space-y-5">
                <!-- Warning -->
                <div class="flex gap-3 rounded-md border border-warning bg-warning/10 p-4">
                    <UIcon name="i-lucide-triangle-alert" class="size-5 shrink-0 text-warning" />

                    <div class="space-y-1">
                        <p class="font-medium text-highlighted">
                            You're about to void this job order.
                        </p>
                        <p class="text-sm text-muted">
                            The job order will no longer be treated as active and
                            will appear on the Voided Jobs page.
                        </p>
                    </div>
                </div>

                <!-- Reason -->
                <UFormField label="Reason for voiding" required
                    help="Please provide a reason so this action can be tracked.">
                    <UTextarea v-model="voidReason" class="w-full" :rows="3"
                        placeholder="e.g. Customer cancelled the order" />
                </UFormField>

                <!-- Actions -->
                <div class="flex justify-end gap-2 pt-2">
                    <UButton label="Cancel" color="neutral" variant="outline" @click="isVoidConfirmOpen = false" />

                    <UButton label="Confirm Void" icon="i-lucide-x" color="error" :disabled="!voidReason.trim()"
                        @click="voidJob" />
                </div>
            </div>
        </template>
    </UModal>
    <AddJobItemForm v-model:is-open="isAddItemFormOpen" :jo-number="reviewData?.entity.jo_number"
        :editing-item="selectedJobItem" @save="saveJobItem" />
    <PaymentForm v-model:is-open="isAddPaymentFormOpen" :balance="Number(reviewData?.entity.balance ?? 0)"
        @save="savePayment" />
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
            <OrderSummary :job-order="reviewData.entity" />
            <JobItemTable :job-items="reviewData.entity.job_items" :jo-number="reviewData.entity.jo_number" :highlighted-item-id="highlightedItemId">
                <template #header-actions>
                    <UTooltip
                        :text="!reviewData.entity.jo_number ? 'A valid job order number is required' : 'Add an item'">
                        <span>
                            <UButton @click="() => isAddItemFormOpen = true"
                                :disabled="!reviewData.entity.jo_number || reviewData.entity.jo_number <= 0"
                                icon="i-lucide-plus" label="Add Item" variant="outline" />
                        </span>
                    </UTooltip>
                </template>
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditItemForm(item)" />
                </template>
            </JobItemTable>
            <PaymentTable :payments="reviewData.entity.payments" :balance="Number(reviewData?.entity.balance)"
                @open-form="() => isAddPaymentFormOpen = true" />
            <div class="grid grid-cols-2 gap-4">
                <UButton label="Void Job Order" icon="i-lucide-x" color="neutral" variant="outline" size="lg"
                    class="flex w-full justify-center" @click="() => isVoidConfirmOpen = true" />
                <UButton label="Confirm and mark as resolved" icon="i-lucide-check" class="flex w-full justify-center"
                    @click="confirmResolution" />
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