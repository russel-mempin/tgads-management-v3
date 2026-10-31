<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import type { Transfer } from '@/types/transfer';

const authStore = useAuthStore()

// UI Variables
const loading = ref(false)
const isAddTransferFormOpen = ref(false)

// Data Variables
const selectedTransfer = ref<Transfer>()

// Filtering
const descriptionSearch = ref('')
const includeArchived = ref(false)

// UI Functions
const openAddTransferForm = () => {
    isAddTransferFormOpen.value = true
}

// Data Functions
</script>

<template>
    <div class="h-full min-h-0 flex flex-col">
        <section class="shrink-0 mt-6 px-6 flex gap-6 items-center">
            <UInput size="lg" class="flex-1" v-model="descriptionSearch" placeholder="Search by description" />
            <USwitch v-if="authStore.isOwner" label="Include archived" v-model="includeArchived" />
            <UButton label="Add Transfer" icon="i-lucide-plus" color="primary" size="lg"
                @click="openAddTransferForm" />
        </section>
        <section class="bg-default flex-1 min-h-0 m-6 border border-default rounded-md overflow-hidden">
            <!-- <MiscSaleTable :misc-sale="data">
                <template #actions="{ item }">
                    <UButton icon="i-lucide-square-pen" variant="ghost" size="md" @click="openEditMiscSaleForm(item)" />
                    <UButton icon="i-lucide-eye-off" variant="ghost" color="error" size="md"
                        @click="openDeleteMiscSaleModal(item)" />
                </template>
            </MiscSaleTable> -->
        </section>
        <!-- <section class="shrink-0 mb-6 px-6 flex items-center justify-between">
            <p class="text-muted text-sm">
                Showing
                {{ data.length ? currentOffset + 1 : 0 }}–{{
                    Math.min(currentOffset + data.length, totalRecords)
                }}
                of {{ totalRecords }}
            </p>

            <UPagination v-model:page="currentPage" :total="totalRecords" :items-per-page="rows" />
        </section> -->
    </div>
</template>