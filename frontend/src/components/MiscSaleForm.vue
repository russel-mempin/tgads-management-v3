<script setup lang="ts">
const amount = defineModel<number>('amount', { required: true })
const date = defineModel<string>('date', { required: true })
const description = defineModel<string>('description', { required: true })
</script>

<template>
	<section class="flex flex-col gap-4">
		<div class="grid grid-cols-2 gap-4">
			<UFormField label="Amount">
				<UInputNumber v-model="amount" class="w-full" :increment="false" :decrement="false" :format-options="{
					style: 'currency',
					currency: 'PHP',
					currencyDisplay: 'code',
					currencySign: 'accounting'
				}" disabled @focus="(e: FocusEvent) => (e.target as HTMLInputElement).select()" />
			</UFormField>
			<UFormField label="Date Received">
				<UInput v-model="date" type="datetime-local" class="w-full" disabled />
			</UFormField>
		</div>
		<UFormField label="Description">
			<UTextarea v-model="description" class="w-full" disabled />
		</UFormField>
	</section>
</template>