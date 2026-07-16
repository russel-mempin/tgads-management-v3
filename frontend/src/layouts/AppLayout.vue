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
    <div class="flex flex-1">
        <Sidebar v-model:open="open" />
        <div class="flex-1 flex flex-col">
            <div class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default">
                <UButton icon="i-lucide-panel-left" color="neutral" variant="ghost"
                    :aria-label="open ? 'Close sidebar' : 'Open sidebar'" @click="() => { open = !open }" />
                <h1 class="ml-4 text-lg font-semibold">{{ route.meta.breadcrumb }}</h1>
            </div>
            <p v-if="subtitle" class="bg-elevated border-b border-default text-muted py-2 px-4">
                {{ subtitle }}
            </p>
            <div class="flex-1 p-4">
                <RouterView />
            </div>
        </div>
    </div>
</template>