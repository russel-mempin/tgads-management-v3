<script setup lang="ts">
import { onMounted } from "vue"
import { useAuthStore } from "./stores/auth";
import { useReferenceStore } from "./stores/reference";

const authStore = useAuthStore()
const referenceStore = useReferenceStore()

onMounted(async () => {
  await authStore.initialize()

  if (authStore.user) {
    await referenceStore.initialize()
  }
})
</script>

<template>
  <UApp :toaster="{ position: 'top-center' }">
    <RouterView />
  </UApp>
</template>