<script setup lang="ts">
const props = withDefaults(defineProps<{
    title?: string
    description?: string
    cancelLabel?: string
    confirmLabel?: string
    confirmIcon?: string
    confirmColor?: 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'
    icon?: string
    iconColor?: string
    iconBackground?: string
}>(), {
    title: 'Confirm Action',
    description: 'Are you sure you want to continue?',
    cancelLabel: 'Cancel',
    confirmLabel: 'Confirm',
    confirmIcon: 'i-lucide-check',
    confirmColor: 'primary',
    icon: 'i-lucide-circle-question-mark',
    iconColor: 'text-primary',
    iconBackground: 'bg-primary/10',
})

const isOpen = defineModel<boolean>('isOpen', { required: true })

const emit = defineEmits<{
    confirm: []
}>()


const confirm = () => {
    emit('confirm')
}
</script>

<template>
    <UModal v-model:open="isOpen">
        <template #content>
            <div class="flex flex-col items-center gap-6 p-6">
                <div class="flex flex-col items-center gap-2">
                    <span class="rounded-md p-2" :class="iconBackground">
                        <UIcon :name="icon" class="size-5" :class="iconColor" />
                    </span>

                    <h2 class="text-lg font-semibold">
                        {{ title }}
                    </h2>
                </div>

                <p class="text-center">
                    {{ description }}
                </p>

                <div class="flex w-full gap-2">
                    <UButton class="flex-1 justify-center" size="lg" :label="cancelLabel" icon="i-lucide-x"
                        variant="outline" color="neutral" @click="isOpen = false" />

                    <UButton class="flex-1 justify-center" size="lg" :label="confirmLabel" :icon="confirmIcon"
                        :color="confirmColor" @click="confirm" />
                </div>
            </div>
        </template>
    </UModal>
</template>