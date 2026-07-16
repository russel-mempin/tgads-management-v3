<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, useRoute } from 'vue-router';
import type { BreadcrumbItem } from '@nuxt/ui'
import Sidebar from '@/components/Sidebar.vue';
import { useAuthStore } from '@/stores/auth';

const open = ref(true)
const route = useRoute()
const authStore = useAuthStore()
const breadcrumbItems = computed<BreadcrumbItem[]>(() => {
  const current = route.meta.breadcrumb as string | undefined
  return [
    { label: 'Dashboard', to: '/dashboard' },
    ...(current && current !== 'Dashboard' ? [{ label: current }] : [])
  ]
})
const subtitle = computed(() => {
  const meta = route.meta.subtitle
  if (typeof meta === 'function') return meta(authStore)
  return meta
})
</script>

<template>
    <div class="flex flex-1">
        <Sidebar v-model:open="open" />
        <div class="flex-1 flex flex-col">
            <div class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default">
                <UButton icon="i-lucide-panel-left" color="neutral" variant="ghost" aria-label="Toggle sidebar"
                    @click="() => { open = !open }" />
                <UBreadcrumb class="ml-4" color="neutral" :items="breadcrumbItems" :ui="{ link: 'text-medium' }"/>
            </div>
            <p v-if="subtitle" class="bg-neutral-100 border-b border-default py-2 px-4">{{ subtitle }}</p>
            <div class="flex-1 p-4">
                <RouterView />
            </div>
        </div>
    </div>
</template>