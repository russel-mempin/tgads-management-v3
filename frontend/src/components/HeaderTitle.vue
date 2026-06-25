<script setup lang="ts">
const props = defineProps<{
	title: string
	subtitle: string
}>()
</script>
<template>
	<div>
		<h1 class="text-xl font-semibold">{{ title }}</h1>
		<h2 class="text-gray-800">{{ subtitle }}</h2>
	</div>
</template>