<script setup lang="ts">
import { ref } from 'vue';
import { Button, InputText, Select } from 'primevue';
import { Plus } from '@lucide/vue';

const joNumberSearch = ref('');
const jobStatus = ref('');
const jobStatusOptions = ref(['For Layout', 'For Approval', 'For Printing', 'For Pickup', 'Released', 'Cancelled']);
</script>

<template>
	<section class="flex justify-between items-center">
		<div>
			<h1 class="text-lg font-semibold">Job Orders</h1>
			<h2>View and manage all job orders in the system. Filter data to quickly find relevant orders.</h2>
		</div>
		<Button label="Add Job Order">
			<template #icon>
				<Plus />
			</template>
		</Button>
	</section>
	<section class="my-2 flex gap-2">
		<InputText class="flex-1" v-model="joNumberSearch" placeholder="Search by customer name or JO Number..." />
		<Select v-model="jobStatus" :options="jobStatusOptions" placeholder="Job Status" />
		<Button label="Clear Filters" variant="text">
		</Button>
	</section>
	<section>
		
	</section>
</template>