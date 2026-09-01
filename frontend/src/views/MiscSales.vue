<script setup lang="ts">
import { ref } from 'vue';

const descriptionSearch = ref('')
const includeArchived = ref(false)
</script>

<template>
	<div class="m-6">
		<section class="flex gap-6 items-center">
			<UInput size="lg" class="flex-1" v-model="descriptionSearch"
            placeholder="Search by description" />
			<USwitch label="Include archived" v-model="includeArchived" />
			<UButton label="Add Misc Sale" icon="i-lucide-plus" color="primary" size="lg" />
		</section>
		<section class="mt-6 border border-default bg-default rounded-md">
			
		</section>
	</div>
</template>