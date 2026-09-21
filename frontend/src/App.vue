<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useAuthStore } from "./stores/auth";
import { useReferenceStore } from "./stores/reference";

const authStore = useAuthStore()
const referenceStore = useReferenceStore()

const initialized = ref(false)

onMounted(async () => {
  await authStore.initialize()

  if (authStore.user) {
    await referenceStore.initialize()
  }
  initialized.value = true
})
</script>

<template>
  <UApp :toaster="{ position: 'top-center' }">
    <RouterView v-if="initialized"/>
  </UApp>
</template>