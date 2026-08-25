<script setup lang="ts">
const amount = defineModel<number>('amount', { required: true })
const date = defineModel<string>('date', { required: true })
const description = defineModel<string>('description', { required: true })
</script>

<template>
	<section class="flex flex-col gap-4">
		<div class="grid grid-cols-2 gap-4">
			<UFormField label="Amount" required>
				<UInputNumber v-model="amount" class="w-full" :increment="false" :decrement="false" :format-options="{
					style: 'currency',
					currency: 'PHP',
					currencyDisplay: 'code',
					currencySign: 'accounting'
				}" @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
			</UFormField>
			<UFormField label="Date" required>
				<UInput v-model="date" type="datetime-local" class="w-full" />
			</UFormField>
		</div>
		<UFormField label="Description" required>
			<UTextarea v-model="description" class="w-full" />
		</UFormField>
	</section>
</template>