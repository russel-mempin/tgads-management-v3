<script setup lang="ts">
// Dependencies
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
// API Calls
import { getAllServices } from '@/api/services';
// Types
import type { Service } from '@/types/service';
// Components
import ServicesTable from '@/components/ServicesTable.vue';

const router = useRouter()

// Data Variables
const data = ref<Service[]>([])
const includeInactive = ref(false)

// UI Variable
const loading = ref(false)

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        data.value = await getAllServices(includeInactive.value)
    }
    finally {
        loading.value = false
    }
}

onMounted(fetchData)
watch(includeInactive, async () => {
    await fetchData()
})
</script>

<template>
    <div class="h-full min-h-0 flex flex-col gap-6 p-6 ">
        <section class="shrink-0 flex items-center gap-6">
            <UInput placeholder="Search by service name..." size="lg" class="flex-1" />
            <USwitch v-model="includeInactive" label="Include inactive" size="lg" />
            <UButton label="Add Service" size="lg" @click="() => router.push('/manage-services/add')"
                icon="i-lucide-plus" />
        </section>
        <section class="bg-default flex-1 min-h-0 border border-default rounded-md overflow-hidden">
            <ServicesTable :services="data" />
        </section>
    </div>
</template>