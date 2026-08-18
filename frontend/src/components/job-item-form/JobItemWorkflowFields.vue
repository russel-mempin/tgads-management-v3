<script setup lang="ts">
import type { JobStatus } from '@/types/jobOrder';
import { JOB_STATUSES } from '@/utils/constants';

const jobStatus = defineModel<JobStatus>('jobStatus', { required: true })
const dueDate = defineModel<string>('dueDate', { required: true })
const description = defineModel<string | undefined>('description')
const notes = defineModel<string | undefined>('notes')
</script>

<template>
    <div class="grid grid-cols-2 gap-6">
        <UFormField label="Job Status" class="w-full">
            <USelect v-model="jobStatus" :items="JOB_STATUSES" class="w-full" />
        </UFormField>
        <UFormField label="Due Date" required>
            <UInput v-model="dueDate" type="datetime-local" class="w-full" />
        </UFormField>
        <UFormField label="Description" class="w-full">
            <UInput v-model="description" class="w-full" />
        </UFormField>
        <UFormField label="Notes" class="w-full">
            <UInput v-model="notes" class="w-full" />
        </UFormField>
    </div>
</template>