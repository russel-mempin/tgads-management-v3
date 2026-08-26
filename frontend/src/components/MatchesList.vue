<script setup lang="ts">
import type { PossibleMatch } from '@/types/forReview';
import { formatJobItem, matchPercentageClass, matchPercentage, formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	matchesList: PossibleMatch[]
}>()

const selectedMatchId = defineModel<string | null>('selectedMatchId', { required: true })
</script>

<template>
	<div class="flex flex-col gap-2">
		<div v-for="match in matchesList" :key="match.id" @click="selectedMatchId = match.id"
			:class="[
				'rounded-sm border px-4 py-2 flex justify-between mb-2 cursor-pointer transition-colors',
				selectedMatchId === match.id
					? 'border-primary bg-primary/10'
					: 'border-default hover:bg-elevated'
			]">
			<div class="flex flex-col justify-between">
				<p class="font-semibold text-highlighted">{{ match.jo_number }}</p>
				<p>{{ match.customer_name }}</p>

				<div class="flex gap-2">
					<p v-for="item in match.job_items" :key="item.item_id">
						{{ formatJobItem(item) }}
					</p>
				</div>
			</div>

			<div class="text-right">
				<p class="font-semibold" :class="matchPercentageClass(match.match_score)">
					{{ matchPercentage(match.match_score) }}% match
				</p>

				<p>Balance: {{ formatCurrency(match.remaining_balance) }}</p>

				<div class="mt-2 flex gap-2 justify-end">
					<p v-for="matchReason in match.match_reasons" :key="matchReason"
						class="w-fit uppercase text-xs font-semibold rounded-md px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300">
						{{ matchReason }}
					</p>
				</div>
			</div>
		</div>
	</div>
</template>