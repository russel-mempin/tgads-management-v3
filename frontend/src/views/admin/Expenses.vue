<script setup lang="ts">
import { ref } from 'vue'
import { Button } from 'primevue';
import { Plus } from '@lucide/vue';

const isVisible = ref(false);
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Expenses</h1>
			<h2>Track your business expenses and monitor spending trends. Filter by month and year to review and compare
				expenses across different periods.</h2>
		</div>
		<Button label="Add Expense" @click="isVisible = true">
			<template #icon>
				<Plus />
			</template>
		</Button>
	</section>
	<section class="mt-4 flex-1 h-full rounded-md border border-slate-300 overflow-hidden bg-white">
	
	</section>
</template>