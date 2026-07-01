<script setup lang="ts">
import HeaderTitle from '@/components/HeaderTitle.vue';
import { ref } from 'vue';
import { DatePicker, Button } from 'primevue';
import { Calendar } from '@lucide/vue'

const selectedDate = ref(new Date);
const reportDate = ref();

</script>
<template>
	<div class="mx-12 my-6 flex flex-col h-full min-h-0">
		<section class="flex justify-between items-center">
			<HeaderTitle title="Daily Collection"
				subtitle="Review payments and expenses recorded each day to track daily sales and cash flow. Select a report day to view data." />
		</section>
		<section class="mt-6 flex items-center gap-4 bg-white p-4 rounded-lg border border-gray-200 shadow-xs">
			<div class="relative flex-1">
				<div
					class="absolute left-1.5 top-1/2 -translate-y-1/2 z-10 flex items-center justify-center w-7 h-7 rounded-md bg-blue-100">
					<Calendar class="size-4 text-blue-600" />
				</div>
				<DatePicker v-model="selectedDate" :maxDate="new Date()" dateFormat="M dd, yy" fluid
					class="date-input-with-icon" />
			</div>
			<Button label="Today" variant="outlined" @click="selectedDate = new Date()" />
		</section>
		<section class="bg-white p-4">
			<p>P</p>
		</section>
	</div>
</template>

<style scoped>
:deep(.date-input-with-icon input) {
	padding-left: 3rem;
}
</style>