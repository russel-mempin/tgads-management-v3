<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getAllExtras } from '@/api/extras';
import ExtrasTable from '@/components/ExtrasTable.vue';
import type { Extra } from '@/types/extra';

const data = ref<Extra[]>([])

// UI Variable
const loading = ref(false)

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
</script>

<template>
    <section class="m-6 flex items-center gap-6">
        <UInput placeholder="Search by extra name..." class="flex-1"/>
        <UButton label="Add Extra" icon="i-lucide-plus"/>
    </section>
    <section class="m-6 bg-default border-default border rounded-md">
        <ExtrasTable :extra="data"/>
    </section>
</template>