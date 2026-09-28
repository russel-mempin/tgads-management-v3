<script setup lang="ts">
import { reactive, watch } from 'vue';
import { z } from 'zod';
import type { Extra, ExtraCreate } from '@/types/extra';
import type { FormSubmitEvent } from '@nuxt/ui';

const isOpen = defineModel<boolean>('isOpen', { required: true })

const props = defineProps<{
    editingExtra?: Extra | null
}>()

const emit = defineEmits<{
    save: [extra: ExtraCreate]
}>()

const schema = z.object({
    name: z.string().min(1, 'Name is required'),
    price: z.number({ error: 'Price is required' }).positive('Price must be greater than 0'),
    status: z.boolean(),
})
type Schema = z.output<typeof schema>

const getInitialState = (): Schema => ({
    name: '',
    price: 1,
    status: true,
})
const state = reactive<Schema>(getInitialState())

const resetForm = () => {
	Object.assign(state, getInitialState())
}
const handleCancel = () => {
    resetForm()
    isOpen.value = false
}

// Data Functions
watch([() => props.editingExtra, isOpen], ([extra, open]) => {
    if (open && extra) {
        Object.assign(state, {
            name: extra.name,
            price: Number(extra.price),
            status: extra.is_active,
        })
    } 
	else {
        resetForm()
    }
})
const onSubmit = (event:FormSubmitEvent<Schema>) => {
    const payload: ExtraCreate = {
        name: event.data.name,
        price: event.data.price,
        is_active: event.data.status,
    }
    emit('save', payload)
    resetForm()
    isOpen.value = false
}
</script>

<template>
    <UModal 
        :title="editingExtra ? 'Edit Extra' : 'Add Extra'"
        v-model:open="isOpen"
        description="Enter information about the extra service and save to database."
        :close="{ color: 'error', class: 'rounded-full'}"
    >
        <template #body>
            <UForm :schema="schema" v-model:state="state" @submit="onSubmit">
                <UFormField label="Name" required>
                    <UInput v-model="state.name" class="w-full" placeholder="Layout"/>
                </UFormField>
                <div class="grid grid-cols-2 gap-6 mt-6">
                    <UFormField label="Price" required>
                        <UInputNumber 
                            v-model="state.price"
                            :increment="false"
                            :decrement="false"
                            :format-options="{
                                style: 'currency',
                                currency: 'PHP',
                                currencyDisplay: 'code',
                                currencySign: 'accounting'
                            }"
                            @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()"
                        />
                    </UFormField>
                    <UFormField label="Status" class="flex flex-col justify-evenly" required>
                        <div class="flex gap-2">
                            <USwitch v-model="state.status" />
                            <p>{{ state.status ? 'Active' : 'Inactive' }}</p>
                        </div>
                    </UFormField>
                </div>
                <div class="flex justify-end gap-6 mt-6">
					<UButton label="Cancel" icon="i-lucide-x" color="neutral" variant="outline" size="lg" class="w-28 justify-center"
						@click="handleCancel" />
					<UButton label="Save" icon="i-lucide-save" color="primary" size="lg" class="w-28 font-semibold justify-center items-center"
						type="submit" />
				</div>
            </UForm>
        </template>
    </UModal>
</template>