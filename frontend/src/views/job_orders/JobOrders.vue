<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getJobOrderKpis } from '@/api/job_orders'

const authStore = useAuthStore()
const kpis = ref<Record<string, any>>({})
const activeFilter = ref<string | null>(null)

onMounted(async () => {
    // fetchServices()
    kpis.value = await getJobOrderKpis()
})

const clearFilters = () => {
    // joNumberSearch.value = ''
    // jobStatus.value = ''
    // paymentStatus.value = ''
    // currentOffset.value = 0
    // fetchServices()
}

const setFilter = (filter: string) => {
    activeFilter.value = activeFilter.value === filter ? null : filter
    clearFilters()
}
</script>

<template>
    <!-- Operation KPI's -->
    <section v-if="authStore.isLoggedIn" class="grid grid-cols-4 gap-4">
        <div @click="setFilter('overdue')"
            class="border border-gray-200 shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'overdue' ? 'bg-orange-100' : 'bg-white hover:bg-orange-50'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-orange-700"
                :class="activeFilter === 'overdue' ? 'bg-orange-300' : 'bg-orange-100'">
                <UIcon name="i-lucide-file-warning" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-gray-600">Overdue Jobs</p>
                <p class="font-bold text-3xl text-orange-700">{{ kpis.overdue_jobs }}</p>
            </div>
        </div>
        <div @click="setFilter('in-progress')"
            class="border border-gray-200 shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'in-progress' ? 'bg-blue-100' : 'bg-white hover:bg-red-50'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-blue-700"
                :class="activeFilter === 'in-progress' ? 'bg-blue-300' : 'bg-blue-100'">
                <UIcon name="i-lucide-clock" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-gray-600">In Progress</p>
                <p class="font-bold text-3xl text-blue-700">{{ kpis.in_progress }}</p>
            </div>
        </div>
        <div @click="setFilter('due-today')"
            class="border border-gray-200 shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'due-today' ? 'bg-yellow-100' : 'bg-white hover:bg-yellow-50'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-red-700"
                :class="activeFilter === 'due-today' ? 'bg-yellow-300' : 'bg-yellow-100'">
                <UIcon name="i-lucide-clock-fading" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-gray-600">Due Today</p>
                <p class="font-bold text-3xl text-red-700">{{ kpis.due_today }}</p>
            </div>
        </div>
        <div @click="setFilter('for-pickup')"
            class="border border-gray-200 shadow-xs p-4 rounded-md flex items-center cursor-pointer transition-all hover:-translate-y-1 hover:shadow-md"
            :class="activeFilter === 'for-pickup' ? 'bg-green-100' : 'bg-white hover:bg-green-50'">
            <div class="flex items-center justify-center w-12 h-12 rounded-full text-green-700"
                :class="activeFilter === 'for-pickup' ? 'bg-green-300' : 'bg-green-100'">
                <UIcon name="i-lucide-printer-check" class="size-6" />
            </div>
            <div class="ml-4">
                <p class="uppercase font-semibold text-sm text-gray-600">Ready for pickup</p>
                <p class="font-bold text-3xl text-green-700">{{ kpis.ready_for_pickup }}</p>
            </div>
        </div>
    </section>
    <!-- Controls -->
    <section class="mt-4 flex gap-4">
        <UInput size="lg" class="flex-1" v-model="joNumberSearch" placeholder="Search by customer name or JO Number..." />
        <USelect size="lg" class="w-50" v-model="jobStatus" :options="jobStatusOptions" placeholder="Job Status" showClear />
        <USelect size="lg" class="w-50" v-model="paymentStatus" :options="paymentStatusOptions" placeholder="Payment Status"
            showClear />
        <UButton size="lg" icon="i-lucide-funnel-x" label="Clear Filters" color="neutral" variant="soft" @click="clearFilters" />
        <UButton size="lg" icon="i-lucide-file-plus-corner" label="Add Job Order" color="primary" variant="solid" @click="clearFilters" />
    </section>
</template>