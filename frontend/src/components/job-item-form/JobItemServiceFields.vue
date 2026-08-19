<script setup lang="ts">
import { computed } from 'vue' 
import type { Service } from '@/types/service';
import type { SizeUnit } from '@/types/jobOrder';
import { MEASUREMENT_UNITS } from '@/utils/constants';

const props = defineProps<{
    services: Service[]
    isAreaBased: boolean
    selectedServiceData?: Service
}>()

const service = defineModel<string>('service', { required: true })
const option = defineModel<string>('option', { required: true })
const width = defineModel<number | undefined>('width')
const height = defineModel<number | undefined>('height')
const unit = defineModel<SizeUnit | undefined>('unit')
const quantity = defineModel<number>('quantity', { required: true })

const applicableOptions = computed(() =>
    props.selectedServiceData?.options ?? []
)
</script>

<template>
    <div class="grid grid-cols-2 gap-6">
        <UFormField label="Service/Product" name="selectedService" required class="w-full">
            <UInputMenu v-model="service" value-key="id" label-key="name" :items="props.services"
                class="w-full" />
        </UFormField>
        <UFormField label="Variant" name="selectedOption" required class="w-full">
            <USelect v-model="option" value-key="id" label-key="name" :items="applicableOptions"
                class="w-full" />
        </UFormField>
    </div>
    <!-- Size Input for Area Based -->
    <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
        <div v-if="isAreaBased" class="grid grid-cols-4 gap-6">
            <UFormField label="Width" name="width" required class="w-full">
                <UInputNumber v-model="width" :increment="false" :decrement="false" :step="0.1"
                    :step-snapping="false" :format-options="{ minimumFractionDigits: 1 }" class="w-full"
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
            </UFormField>
            <UFormField label="Height" name="height" required class="w-full">
            <UInputNumber v-model="height" :increment="false" :decrement="false" :step="0.1"
                    :step-snapping="false" :format-options="{ minimumFractionDigits: 1 }" class="w-full"
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
            </UFormField>
            <UFormField label="Unit" name="unit" required class="w-full">
                <UInputMenu v-model="unit" :items="MEASUREMENT_UNITS" label-key="label" value-key="value" class="w-full" />
            </UFormField>
            <UFormField label="Quantity" required class="w-full">
                <UInputNumber v-model="quantity" :min="1" class="w-full"
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
            </UFormField>
        </div>
    </Transition>
    <!-- Quantity Input for Non Area Based -->
    <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
        <div v-if="!isAreaBased">
            <UFormField label="Quantity" required class="w-full">
                <UInputNumber v-model="quantity" :min="1" class="w-full"
                    @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
            </UFormField>
        </div>
    </Transition>
</template>