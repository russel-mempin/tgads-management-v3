<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
</script>

<template>
    <div class="bg-slate-100 flex h-screen overflow-hidden">
        <Navbar class="h-screen" />
        <main class="flex-1 flex flex-col min-h-0 overflow-y-auto">
            <RouterView />
        </main>
    </div>
</template>