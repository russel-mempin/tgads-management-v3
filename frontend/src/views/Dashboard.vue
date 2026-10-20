<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { getOwnerDashboard } from '@/api/dashboards';
import type { OwnerDashboard } from '@/types/dashboard';
import { formatCurrency } from '@/utils/formatters';
import SalesPerService from '@/components/SalesPerService.vue';

const authStore = useAuthStore()

// UI Variables
const loading = ref(false)
const ownerData = ref<OwnerDashboard>()
const totalBalance = computed(() =>
    ownerData.value?.accounts_balances.reduce(
        (total, account) => total + Number(account.current_balance),
        0
    )
);

// Data Functions
const fetchData = async () => {
    loading.value = true
    try {
        ownerData.value = await getOwnerDashboard()
    }
    finally {
        loading.value = false
    }
}
onMounted(fetchData)
</script>

<template>
    <div class="m-6 flex flex-col min-h-0">
        <div v-if="authStore.isOwner && ownerData" class="flex flex-col gap-6">
            <div class="grid grid-cols-[2fr_1fr] gap-6">
                <section>
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-1 h-6 bg-blue-600 rounded-r-full"></div>
                        <p class="text-sm font-semibold montserrat text-highlighted">ACCOUNT RUNNING BALANCES</p>
                    </div>
                    <div>
                        <p>{{ formatCurrency(totalBalance) }}</p>
                    </div>
                </section>
                <section>
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-1 h-6 bg-orange-600 rounded-r-full"></div>
                        <p class="text-sm font-semibold montserrat text-highlighted">PRODUCTION</p>
                    </div>
                    <div class="flex flex-col gap-6">
                        <div
                            class="bg-default border border-slate-200 border-l-4 border-l-orange-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                            <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Overdue Jobs</p>
                            <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">
                                {{ ownerData?.overdue_jobs }}</p>
                        </div>
                        <div
                            class="bg-default border border-slate-200 border-l-4 border-l-orange-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                            <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Pending Jobs</p>
                            <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">
                                {{ ownerData?.pending_jobs }}</p>
                        </div>
                    </div>
                </section>
            </div>
            <!-- Financial -->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-violet-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">FINANCIAL</p>
                </div>
                <div class="grid grid-cols-4 gap-6">
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Collected Today</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">{{
                            formatCurrency(Number(ownerData?.collections_today)) }}</p>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Collected This Month
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">{{
                            formatCurrency(Number(ownerData?.collections_this_month)) }}</p>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Outstanding Receivables
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">
                            {{ formatCurrency(Number(ownerData?.outstanding_receivables)) }}</p>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Expenses This Month</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">
                            {{ formatCurrency(Number(ownerData?.expenses_this_month)) }}</p>
                    </div>
                </div>
            </section>
            <!-- Sales-->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-green-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">SALES PER SERVICE</p>
                </div>
                <div class="bg-default border border-slate-200 border-l-4 border-l-green-600 rounded-lg">
                    <SalesPerService :data="ownerData.sales_per_service" />
                </div>
            </section>
        </div>
    </div>
</template>