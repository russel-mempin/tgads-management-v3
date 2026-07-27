<script setup lang="ts">
import { ref } from 'vue'

// Components
import JobItemForm from './JobItemForm.vue';

// UI Variables
const isOpen = ref(false)

const props = defineProps<{
    joNumber: number
    jobItems: any[]
}>()
</script>

<template>
    <JobItemForm v-model:isOpen="isOpen" />
    <div class="bg-default border border-default rounded-md p-6 m-8">
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center gap-2">
                <UIcon name="i-lucide-briefcase" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
                <p class="font-semibold text-highlighted">Job Items</p>
            </div>
            <UTooltip text="Input a JO Number first." :disabled="!!joNumber">
                <UButton @click="() => { isOpen = true }" :disabled="!joNumber" label="Add Item" icon="i-lucide-plus" />
            </UTooltip>
        </div>
        <!-- Empty state -->
        <div v-if="!jobItems.length" class="flex flex-col items-center justify-center py-12 text-center px-6">
            <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-3">
                <UIcon name="i-lucide-package-open" class="size-6 text-muted" />
            </div>
            <p class="font-medium text-highlighted mb-1">No items yet</p>
            <p class="text-sm text-muted">Click "Add Item" to start building this job order.</p>
        </div>
    </div>
</template>