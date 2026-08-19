<script setup lang="ts">
import type { Extra } from '@/types/service';
import type { JobItemExtraCreate } from '@/types/jobOrder'

const props = defineProps<{
    extraList: Extra[]
}>()

const extras = defineModel<JobItemExtraCreate[]>('extras', { required: true })

// UI Functions
const getExtraPrice = (extra: JobItemExtraCreate) => {
    const extraData = props.extraList.find(x => x.id === extra.extra_service_id)
    if (!extraData) return 0
    return extraData.price * extra.quantity
}
const addExtra = () => {
    extras.value.push({ extra_service_id: '', quantity: 1 })
}
const removeExtra = (index: number) => {
    extras.value.splice(index, 1)
}
</script>

<template>
    <div class="border border-default bg-muted rounded-md">
        <div class="flex items-center justify-between p-4">
            <p class="uppercase font-bold">Extras</p>
            <UButton label="Add Extra" variant="subtle" icon="i-lucide-plus" @click="addExtra" />
        </div>
        <div v-if="!extras.length" class="p-4 text-sm text-muted text-center">
            No extras added.
        </div>
        <div v-for="(extra, index) in extras" :key="index"
            class="grid grid-cols-[1fr_1fr_auto_auto] gap-4 items-end p-4 border-b border-default last:border-b-0">
            <UFormField label="Extra">
                <USelect v-model="extra.extra_service_id" value-key="id" label-key="name" :items="extraList"
                    class="w-full" />
            </UFormField>
            <UFormField label="Quantity">
                <UInputNumber v-model="extra.quantity" :min="1" class="w-full" />
            </UFormField>
            <UFormField label="Price (Auto computed)">
                <UInput :model-value="`₱ ${getExtraPrice(extra)}`" disabled readonly />
            </UFormField>
            <UButton icon="i-lucide-trash-2" color="error" variant="ghost" @click="removeExtra(index)" />
        </div>
    </div>
</template>