<script setup lang="ts">
// Dependencies
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// API Calls
import { getAllServices } from '@/api/services';
// Types
import type { Service } from '@/types/service';
// Components
import ServicesTable from '@/components/ServicesTable.vue';

const router = useRouter()

const data = ref<Service[]>([])

// UI Variable
const loading = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllServices()
    }
    finally {
        loading.value = false
    }
}

onMounted(fetchData)
</script>

<template>
    <section class="m-6 flex items-center gap-6">
        <UInput placeholder="Search by service name..." class="flex-1"/>
        <UButton label="Add Service" @click="() => router.push('/manage-services/add')" icon="i-lucide-plus"/>
    </section>
    <section class="m-6 bg-default border-default border rounded-md">
        <ServicesTable :services="data" />
    </section>
</template>