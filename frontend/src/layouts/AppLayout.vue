<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';

const open = ref(true)
</script>

<template>
    <div class="flex flex-1">
        <Sidebar v-model:open="open" />
        <div class="flex-1 flex flex-col">
            <div class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default">
                <UButton icon="i-lucide-panel-left" color="neutral" variant="ghost" aria-label="Toggle sidebar"
                    @click="() => { open = !open }" />
            </div>
            <div class="flex-1 p-4">
                <RouterView />
            </div>
        </div>
    </div>
</template>