<script setup lang="ts">
// Dependency imports
import { ref, onMounted } from 'vue';
// API call imports
import { getAllExtras, createExtra } from '@/api/extras';
// Component imports
import ExtrasTable from '@/components/ExtrasTable.vue';
import ExtraForm from '@/components/ExtraForm.vue';
import { useReferenceStore } from '@/stores/reference';
// Type imports
import type { Extra, ExtraCreate } from '@/types/extra';

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
</script>

<template>
    <ExtraForm v-model:isOpen="isExtraFormOpen" @save="saveExtraToDb" :editing-extra="selectedExtra" />
    <section class="m-6 flex items-center gap-6">
        <UInput placeholder="Search by extra name..." class="flex-1"/>
        <UButton label="Add Extra" @click="() => isExtraFormOpen = true" icon="i-lucide-plus"/>
    </section>
    <section class="m-6 bg-default border-default border rounded-md">
        <ExtrasTable :extra="data" @edit-extra="openEditForm" />
    </section>
</template>