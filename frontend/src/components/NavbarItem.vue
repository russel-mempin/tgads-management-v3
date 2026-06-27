<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'
import type { Component } from 'vue'

type Props = {
	to: string
	label: string
	icon: Component
}
const props = defineProps<Props>()

const route = useRoute()
const isParentActive = computed(() => route.path === props.to || route.path.startsWith(props.to + '/'))

</script>

<template>
	<RouterLink :to="props.to" v-slot="{ href, navigate, isActive }">
		<a :href="href" @click="navigate" class="flex items-center justify-start gap-3 px-4 py-3 hover:bg-blue-100 rounded-md transition-colors"
			:class="[
				(isActive || isParentActive) ? 'bg-blue-100 text-blue-700 font-semibold' : 'text-gray-600',
			]">
			<component :is="icon" class="w-[20px]" />
			<p class="transition-all duration-300 overflow-hidden">
				{{ props.label }}
			</p>
		</a>
	</RouterLink>
</template>