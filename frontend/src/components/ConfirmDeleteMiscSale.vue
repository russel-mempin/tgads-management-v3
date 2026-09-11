<script setup lang="ts">
defineProps<{
    open: boolean
    title: string
    description: string
}>()

const emit = defineEmits<{
    'update:open': [value: boolean]
    confirm: []
}>()
</script>

<template>
    <UModal :open="open" @update:open="emit('update:open', $event)">
        <template #content>
            <div class="flex flex-col items-center gap-4 p-5">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-red-100">
                    <UIcon name="i-lucide-triangle-alert" class="size-5 text-red-500" />
                </div>

                <div class="text-center">
                    <p class="font-semibold text-highlighted">{{ title }}</p>
                    <p class="mt-1 text-sm text-muted">{{ description }}</p>
                </div>

                <!-- Details supplied by parent -->
                <div class="w-full rounded-lg border border-default bg-elevated p-3">
                    <slot name="details" />
                </div>

                <p class="text-sm font-medium text-highlighted">
                    Are you sure?
                </p>
            </div>

            <div class="flex items-center gap-4 p-4">
                <UButton class="flex-1 justify-center" size="lg" label="No, cancel" variant="outline" color="neutral"
                    icon="i-lucide-x" @click="emit('update:open', false)" />

                <UButton class="flex-1 justify-center" size="lg" label="Yes, delete" color="error"
                    icon="i-lucide-trash-2" @click="emit('confirm')" />
            </div>
        </template>
    </UModal>
</template>