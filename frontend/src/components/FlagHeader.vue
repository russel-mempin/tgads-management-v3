<script setup lang="ts">
import { computed } from 'vue'
import type { ForReview } from '@/types/forReview'
import { getReviewCategoryColor, formatDate } from '@/utils/formatters'

const props = withDefaults(defineProps<{
	flagData: ForReview
	referenceLabel?: string
	icon?: string
}>(), {
	referenceLabel: '',
	icon: 'i-lucide-triangle-alert',
})

const categoryColor = computed(() =>
	getReviewCategoryColor(props.flagData.reason_category)
)

const daysSinceFlagging = computed(() => {
	const createdAt = new Date(props.flagData.created_at)
	const now = new Date()

	const diffMs = now.getTime() - createdAt.getTime()

	return Math.floor(diffMs / (1000 * 60 * 60 * 24))
})
</script>

<template>
	<section class="border rounded-md flex p-4" :class="{
		'border-warning bg-warning/10': categoryColor === 'warning',
		'border-error bg-error/10': categoryColor === 'error',
		'border-info bg-info/10': categoryColor === 'info',
		'border-neutral bg-default': categoryColor === 'neutral',
	}">
		<div class="w-16 h-16 flex items-center justify-center border rounded-full mr-4" :class="{
			'border-warning text-warning': categoryColor === 'warning',
			'border-error text-error': categoryColor === 'error',
			'border-info text-info': categoryColor === 'info',
			'border-neutral text-neutral': categoryColor === 'neutral',
		}">
			<UIcon :name="icon" class="w-8 h-8" />
		</div>

		<div class="flex flex-col gap-1">
			<div class="flex items-center gap-2">
				<UBadge :color="categoryColor">
					{{ flagData.reason_category }}
				</UBadge>
				<p v-if="referenceLabel">
					{{ referenceLabel }} - {{ flagData.entity_reference ? flagData.entity_reference : 'N/A' }}
				</p>
				<p>• &nbsp; flagged {{ daysSinceFlagging }} days ago</p>
			</div>

			<p class="font-semibold text-lg">{{ flagData.reason }}</p>

			<p class="text-muted">Flagged by {{ flagData.created_by_name }} on {{ formatDate(flagData.created_at) }}</p>
		</div>
	</section>
</template>