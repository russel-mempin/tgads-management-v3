<script setup lang="ts">
const isOpen = defineModel<boolean>('isOpen', { required: true })
</script>

<template>
  <UModal
    title="Add Job Item"
    description="Test description"
    v-model:open="isOpen"
  >
    <template #content>
      <p>Test</p>
    </template>
  </UModal>
</template>