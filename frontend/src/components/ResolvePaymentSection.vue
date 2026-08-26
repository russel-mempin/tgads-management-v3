<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useDebounceFn } from '@vueuse/core';
import { searchPossibleJobOrders } from '@/api/forReviews';
import type { PossibleMatch } from '@/types/forReview'
import type { MiscSaleCreate } from '@/types/miscSale'

const props = defineProps<{
    initialMatches: PossibleMatch[]
    entityId: string
}>()

const emit = defineEmits<{
    resolve: [
        value:
        | { type: 'job_order'; match: string }
        | { type: 'misc_sale'; sale: MiscSaleCreate }
    ]
}>()

const resolutionType = ref<'job_order' | 'misc_sale'>('job_order')
const isSearchingManually = ref(false)
const dataToSearch = ref('')
const selectedMatchId = ref<string | null>(null)
const possibleJobOrders = ref<PossibleMatch[]>(props.initialMatches)
const miscSale = ref<MiscSaleCreate>({
    amount: 0,
    date: '',
    description: '',
})
const resolutionNote = ref('')

let latestSearch = ''

const canConfirm = computed(() => {
    if (resolutionType.value === 'job_order') {
        return selectedMatchId.value !== null
    }

    return (
        miscSale.value.amount > 0 &&
        !!miscSale.value.date &&
        !!miscSale.value.description.trim()
    )
})

const backToSuggestions = () => {
    isSearchingManually.value = false
    dataToSearch.value = ''
    if (props.initialMatches) {
        possibleJobOrders.value = props.initialMatches
    }
}

const searchJobOrders = useDebounceFn(async (value: string) => {
    const trimmedValue = value.trim()
    if (!props.entityId) {
        return
    }
    possibleJobOrders.value = props.initialMatches
    const results = await searchPossibleJobOrders(
        props.entityId,
        trimmedValue,
    )
    latestSearch = trimmedValue
    if (latestSearch === trimmedValue) {
        possibleJobOrders.value = results
    }
}, 500)
watch(dataToSearch, (value) => {
    if (!isSearchingManually.value) {
        return
    }
    searchJobOrders(value)
})
watch(
    () => props.initialMatches,
    (matches) => {
        if (!isSearchingManually.value) {
            possibleJobOrders.value = matches
        }
    }
)
const confirmResolution = () => {
    if (resolutionType.value === 'job_order') {
        if (!selectedMatchId.value) return
        emit('resolve', {
            type: 'job_order',
            match: selectedMatchId.value,
        })
        return
    }
    emit('resolve', {
        type: 'misc_sale',
        sale: miscSale.value,
    })
}
</script>

<template>
    <section class="bg-default border border-default rounded-md p-4 flex flex-col gap-4">
        <div class="flex items-center gap-3">
            <UIcon name="i-lucide-square-check-big" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
            <h2 class="text-highlighted font-semibold">Resolve this payment</h2>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <UButton label="Link to Job Order" icon="i-lucide-briefcase" class="flex justify-center py-2"
                :variant="resolutionType === 'job_order' ? 'solid' : 'outline'" @click="resolutionType = 'job_order'" />

            <UButton label="Mark as Misc Sale" icon="i-lucide-receipt-text" class="flex justify-center py-2"
                :variant="resolutionType === 'misc_sale' ? 'solid' : 'outline'" @click="resolutionType = 'misc_sale'" />
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
                    <UInput v-model="dataToSearch" icon="i-lucide-search"
                        placeholder="Search job order number or customer name" class="w-full" />
                    <UButton label="Back to Suggestions" variant="outline" color="neutral" @click="backToSuggestions" />
                </div>
            </div>
            <!-- Form -->
            <MatchesList v-if="resolutionType === 'job_order'" :matches-list="possibleJobOrders"
                v-model:selected-match-id="selectedMatchId" />
            <MiscSaleForm v-else-if="resolutionType === 'misc_sale'" v-model:amount="miscSale.amount"
                v-model:date="miscSale.date" v-model:description="miscSale.description" />
        </div>
        <UFormField label="Resolution note" required>
            <UTextarea v-model="resolutionNote" class="w-full" />
        </UFormField>
        <UButton :disabled="!canConfirm" label="Confirm and mark as resolved" icon="i-lucide-check" class="flex w-full justify-center"
            @click="confirmResolution" />
    </section>
</template>