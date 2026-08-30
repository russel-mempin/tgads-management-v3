<script setup lang="ts">
import { computed } from 'vue';
import type { ForReview } from '@/types/forReview';
import { getReviewCategoryColor, formatDate } from '@/utils/formatters';

const props = defineProps<{
	flagData: ForReview
}>()

const daysSinceFlagging = computed(() => {
	const createdAt = new Date(props.flagData.created_at)
	const now = new Date()

	const diffMs = now.getTime() - createdAt.getTime()
	return Math.floor(diffMs / (1000 * 60 * 60 * 24))
})
</script>

<template>
	<section class="border rounded-md flex p-4" :class="{
		'border-warning bg-warning/10': getReviewCategoryColor(flagData.reason_category) === 'warning',
		'border-error bg-error/10': getReviewCategoryColor(flagData.reason_category) === 'error',
		'border-info bg-info/10': getReviewCategoryColor(flagData.reason_category) === 'info',
		'border-neutral bg-default': getReviewCategoryColor(flagData.reason_category) === 'neutral',
	}">
		<div class="w-16 h-16 flex items-center justify-center border rounded-full mr-4" :class="{
			'border-warning text-warning': getReviewCategoryColor(flagData.reason_category) === 'warning',
			'border-error text-error': getReviewCategoryColor(flagData.reason_category) === 'error',
			'border-info text-info': getReviewCategoryColor(flagData.reason_category) === 'info',
			'border-neutral text-neutral': getReviewCategoryColor(flagData.reason_category) === 'neutral',
		}">
			<UIcon name="i-lucide-triangle-alert" class="w-8 h-8" />
		</div>
		<div class="flex flex-col gap-1">
			<div class="flex items-center gap-2">
				<UBadge :color="getReviewCategoryColor(props.flagData.reason_category)">{{ flagData.reason_category }}
				</UBadge>
				<p>JO - {{ flagData.entity_reference }}</p>
				<p>{{ `• &nbsp; flagged ${daysSinceFlagging} days ago` }}</p>
			</div>
			<p class="font-semibold text-lg">{{ flagData.reason }}</p>
			<p class="text-muted">{{ `Flagged by ${flagData.created_by_name} on ${formatDate(flagData.created_at)}` }}
			</p>
		</div>
	</section>
</template>