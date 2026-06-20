<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
</script>

<template>
    <div id="appBody" class="flex h-screen overflow-hidden">
        <Navbar />
        <div class="w-4/5 flex-1 flex flex-col">
            <main class="flex-1 flex flex-col p-12 min-h-0">
                <div class="flex flex-col h-full overflow-hidden">
                    <RouterView />
                </div>
            </main>
        </div>
    </div>
</template>

<style scoped>
#appBody {
	background: var(--bg-gradient);
}
</style>