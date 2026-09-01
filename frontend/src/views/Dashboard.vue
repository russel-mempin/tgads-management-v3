<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()
const services = [
    { name: 'Digital Printing', count: 88 },
    { name: 'Offset Printing', count: 61 },
    { name: 'Large Format', count: 44 },
    { name: 'Binding & Finishing', count: 29 },
    { name: 'Promotional Items', count: 18 },
]

const max = Math.max(...services.map(s => s.count))
</script>

<template>
    <div class="m-6 flex flex-col min-h-0">
        <div v-if="authStore.isOwner" class="flex flex-col gap-6">
            <!-- Account Balances -->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-blue-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">ACCOUNT RUNNING BALANCES</p>
                    <p class="text-sm montserrat text-muted">3 accounts</p>
                </div>
                <div class="grid grid-cols-3 gap-6">
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted">Cash</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">₱99,999</p>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted">GCash</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">₱99,999</p>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted">RCBC (Cheque)</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted tabular-nums">₱99,999</p>
                    </div>
                </div>
            </section>
            <!-- Financial -->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-violet-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">FINANCIAL</p>
                    <p class="text-sm montserrat text-muted">4 metrics</p>
                </div>
                <div class="grid grid-cols-4 gap-6">
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Sales Today</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">₱99,999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                <ArrowUp class="size-3" />
                                100.0%
                            </span>
                            <span class="text-xs text-muted">vs. yesterday</span>
                        </div>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Sales This Month
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">₱99,999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                <ArrowUp class="size-3" />
                                100.0%
                            </span>
                            <span class="text-xs text-muted">vs. last month</span>
                        </div>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Gross Profit This
                            Month
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">₱99,999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                <ArrowUp class="size-3" />
                                100.0%
                            </span>
                            <span class="text-xs text-muted">31.3% margin</span>
                        </div>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-violet-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Outstanding
                            Receiveables
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">₱99,999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                3 overdue
                            </span>
                            <span class="text-xs text-muted">14 open invoices</span>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Sales-->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-green-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">SALES</p>
                    <p class="text-sm montserrat text-muted">4 metrics</p>
                </div>
                <div class="grid grid-cols-5 gap-6">
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-green-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Orders Today</p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                <ArrowUp class="size-3" />
                                100.0
                            </span>
                            <span class="text-xs text-muted">vs. yesterday</span>
                        </div>
                    </div>
                    <div
                        class="bg-default border border-slate-200 border-l-4 border-l-green-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-3">Average Order Value
                        </p>
                        <p class="text-3xl font-bold tracking-tight text-highlighted mb-2 tabular-nums">₱99,999</p>
                        <div class="flex items-center gap-2">
                            <span
                                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">
                                <ArrowUp class="size-3" />
                                100.0%
                            </span>
                            <span class="text-xs text-muted">vs. yesterday</span>
                        </div>
                    </div>
                    <div
                        class="col-span-3 bg-default border border-slate-200 border-l-4 border-l-green-600 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-4">Orders by Service
                        </p>
                        <div class="flex flex-col gap-3">
                            <div v-for="service in services" :key="service.name" class="grid items-center gap-2.5"
                                style="grid-template-columns: 140px 1fr 32px">
                                <span class="text-xs text-highlighted truncate">{{ service.name }}</span>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-emerald-500 rounded-full opacity-75 transition-all duration-700"
                                        :style="{ width: `${(service.count / max) * 100}%` }" />
                                </div>
                                <span class="text-xs text-muted text-right tabular-nums">{{ service.count }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Production -->
            <section>
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-1 h-6 bg-orange-600 rounded-r-full"></div>
                    <p class="text-sm font-semibold montserrat text-highlighted">PRODUCTION</p>
                    <p class="text-sm montserrat text-muted">2 metrics</p>
                </div>
                <div class="grid grid-cols-2 gap-6">
                    <div
                        class="bg-default border border-default border-l-4 border-l-amber-500 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-4">Jobs Pending</p>
                        <div class="flex items-center gap-4">
                            <div class="w-11 h-11 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
                                <UIcon name="i-lucide-clock" class="size-5 text-amber-500" />
                            </div>
                            <div>
                                <p class="text-3xl font-bold tracking-tight text-amber-500 tabular-nums leading-none">47
                                </p>
                                <p class="text-xs text-muted mt-1">12 due today</p>
                            </div>
                        </div>
                    </div>
                    <div
                        class="bg-default border border-default border-l-4 border-l-amber-500 rounded-lg p-5 hover:shadow-md transition-shadow">
                        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-4">Jobs Completed
                            Today
                        </p>
                        <div class="flex items-center gap-4">
                            <div class="w-11 h-11 rounded-xl bg-green-100 flex items-center justify-center shrink-0">
                                <UIcon name="i-lucide-check" class="size-5 text-green-500" />
                            </div>
                            <div>
                                <p class="text-3xl font-bold tracking-tight text-green-500 tabular-nums leading-none">47
                                </p>
                                <p class="text-xs text-muted mt-1">12 due today</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>