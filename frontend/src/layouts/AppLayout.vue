<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import { useAuthStore } from '@/stores/auth'

const open = ref(true)
const route = useRoute()
const authStore = useAuthStore()

const subtitle = computed(() => {
    const meta = route.meta.subtitle
    if (typeof meta === 'function') return meta(authStore)
    return meta
})
</script>

<template>
    <div class="flex h-dvh">
        <Sidebar v-model:open="open" />
        <div class="flex-1 flex flex-col min-h-0">
            <div
                class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default bg-default/60 backdrop-blur-md">
                <UButton :icon="open ? 'i-lucide-panel-left-close' : 'i-lucide-panel-left-open'" color="neutral"
                    variant="ghost" :aria-label="open ? 'Close sidebar' : 'Open sidebar'" @click="() => { open = !open }" />
                <h1 class="ml-4 text-lg font-semibold">{{ route.meta.breadcrumb }}</h1>
            </div>
            <p v-if="subtitle" class="sticky top-0 z-10 bg-elevated border-b border-default text-muted py-2 px-4">
                {{ subtitle }}
            </p>
            <div class="flex-1 min-h-0 bg-[#fbfbfb] dark:bg-[#132440]">
                <RouterView />
            </div>
        </div>
    </div>
</template>