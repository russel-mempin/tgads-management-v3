<script setup lang="ts">	
const props = defineProps<{
	hasJobItems: boolean
}>()
const joNumber = defineModel<number>('joNumber', { required: true })
const dateReceived = defineModel<string>('dateReceived', { required: true })
</script>

<template>
	<div class="bg-default border border-default rounded-md p-6 m-8">
		<div class="flex items-center gap-2 mb-6">
			<UIcon name="i-lucide-hash" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
			<h2 class="font-semibold text-highlighted">Order Information</h2>
		</div>
		<div class="grid grid-cols-2 gap-6">
			<UFormField label="Job Order No." required>
				<UInput v-model="joNumber" type="number" placeholder="e.g. 19291" size="lg" class="w-full"
					:disabled="hasJobItems" :hint="hasJobItems ? 'Clear all job items to change.' : ''"
					@focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
			</UFormField>
			<UFormField label="Date Received" required>
				<UInput v-model="dateReceived" type="datetime-local" size="lg" class="w-full" />
			</UFormField>
		</div>
	</div>
</template>