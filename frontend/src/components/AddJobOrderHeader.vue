<script setup lang="ts">
const isWalkIn = defineModel<boolean>('isWalkIn', { required: true })
</script>

<template>
	<section class="m-8">
		<div class="flex items-start justify-between">
			<div>
				<p class="text-xs font-semibold uppercase tracking-widest text-primary mb-1">New Entry</p>
				<h1 class="text-2xl font-bold text-highlighted">Add Job Order</h1>
				<p class="text-sm text-muted mt-1">
					Fields marked <span class="text-error font-semibold">*</span> are required.
				</p>
			</div>
			<div class="flex items-center gap-3 bg-elevated border border-default rounded-md px-4 py-3 mt-1">
				<div>
					<p class="text-base font-semibold text-highlighted">Walk-in Customer</p>
					<p class="text-xs text-muted">No customer record needed</p>
				</div>
				<USwitch v-model="isWalkIn" size="lg" />
			</div>
		</div>
	</section>
</template>