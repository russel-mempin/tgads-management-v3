<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
</script>

<template>
	<div id="appBody" class="flex">
		<Navbar />
		<div class="w-4/5 flex-1 flex flex-col">
			<main class="flex-1 p-4">
				<RouterView />
			</main>
		</div>
	</div>
</template>

<style scoped>
#appBody {
  background: var(--bg-gradient);
}
</style>