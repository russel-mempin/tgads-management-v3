<script setup lang="ts">
// Dependency imports
import { ref, onMounted } from 'vue';
import axios from 'axios';
// API call imports
import { getAllExtras, createExtra, updateExtra } from '@/api/extras';
// Component imports
import ExtrasTable from '@/components/ExtrasTable.vue';
import ExtraForm from '@/components/ExtraForm.vue';
import { useReferenceStore } from '@/stores/reference';
// Type imports
import type { Extra, ExtraCreate, ExtraUpdate } from '@/types/extra';

// Data Variables
const data = ref<Extra[]>([])
const referenceStore = useReferenceStore()
const selectedExtra = ref<Extra | null>(null)

// UI Variable
const toast = useToast()
const loading = ref(false)
const isExtraFormOpen = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllExtras()
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
const saveExtraToDb = async (option: ExtraCreate) => {
    loading.value = true
    try {
        await createExtra(option)
        toast.add({
            title: 'Extra Added.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        await fetchData()
        await referenceStore.refresh()
    } 
    catch (error) {
        console.error('Error saving extra:', error)
    }
    finally {
        loading.value = false
    }
}
const openEditForm = (extra: Extra) => {
    selectedExtra.value = extra
    isExtraFormOpen.value = true
}
const saveUpdatedInfoToDb = async (id: string, extra: ExtraUpdate) => {
    loading.value = true
    try {
        await updateExtra(id, extra)
        toast.add({
            title: 'Extra updated.',
            color: 'success',
            icon: 'i-lucide-circle-check'
        })
        fetchData()
        await referenceStore.refresh()
    }
    catch(error: unknown) {
        console.error("Failed to create option:", error)
        let message = "An unexpected error occured."
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
    finally {
        loading.value = false
    }
}
</script>

<template>
    <ExtraForm v-model:isOpen="isExtraFormOpen" @save="saveExtraToDb" @update="saveUpdatedInfoToDb" :editing-extra="selectedExtra" />
    <section class="m-6 flex items-center gap-6">
        <UInput placeholder="Search by extra name..." class="flex-1"/>
        <UButton label="Add Extra" @click="() => isExtraFormOpen = true" icon="i-lucide-plus"/>
    </section>
    <section class="m-6 bg-default border-default border rounded-md">
        <ExtrasTable :extra="data" @edit-extra="openEditForm" />
    </section>
</template>