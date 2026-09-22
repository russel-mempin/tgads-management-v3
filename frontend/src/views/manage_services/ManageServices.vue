<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getAllServices } from '@/api/services';
import ServicesTable from '@/components/ServicesTable.vue';
import type { Service } from '@/types/service';

const data = ref<Service[]>([])

// UI Variable
const loading = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllServices()
        console.log(data.value)
    }
    finally {
        loading.value = false
    }
}

onMounted(fetchData)
</script>

<template>
    <section class="m-4 flex items-center gap-4">
        <UInput placeholder="Search by service name..." class="flex-1"/>
        <UButton label="Add Service" icon="i-lucide-plus"/>
    </section>
    <section class="m-4 bg-default border-default border rounded-md">
        <ServicesTable :services="data" />
    </section>
</template>