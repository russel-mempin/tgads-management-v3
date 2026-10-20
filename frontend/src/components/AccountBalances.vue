<script setup lang="ts">
import { computed } from 'vue';
import type { AccountData } from '@/types/dashboard';
import { formatCurrency } from '@/utils/formatters';

const props = defineProps<{
	data: AccountData[]
}>()

const totalBalance = computed(() =>
	props.data.reduce(
		(sum, account) => sum + Number(account.current_balance),
		0
	)
)

const colors = [
	'bg-blue-500',
	'bg-violet-500',
	'bg-emerald-500',
	'bg-amber-500',
	'bg-rose-500',
	'bg-cyan-500',
]

const accounts = computed(() => {
	const total = props.data.reduce(
		(sum, account) => sum + Math.abs(Number(account.current_balance)),
		0
	)

	return props.data.map((account, index) => {
		const balance = Number(account.current_balance)

		return {
			...account,
			balance,
			percentage: total ? Math.abs(balance) / total * 100 : 0,
			color: colors[index % colors.length],
		}
	})
})
</script>

<template>
	<div class="bg-default border border-slate-200 border-l-4 border-l-blue-600 rounded-lg p-5 hover:shadow-md transition-shadow">
		<div class="mb-3">
			<p class="text-sm text-gray-500">Total Account Balance</p>
			<p class="text-4xl font-bold tabular-nums">
				{{ formatCurrency(totalBalance) }}
			</p>
		</div>
		<div class="space-y-4">
			<!-- Single stacked bar -->
			<div class="flex h-6 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
				<div v-for="account in accounts" :key="account.account_name" :class="account.color"
					:style="{ width: `${account.percentage}%` }"
					:title="`${account.account_name}: ${account.percentage.toFixed(1)}%`"
					class="h-full transition-all duration-300" />
			</div>

			<!-- Account legend -->
			<div class="space-y-3">
				<div v-for="account in accounts" :key="account.account_name"
					class="flex items-center justify-between gap-4">
					<div class="flex min-w-0 items-center gap-2">
						<span class="h-3 w-3 shrink-0 rounded-sm" :class="account.color" />
						<span class="truncate">{{ account.account_name }}</span>
					</div>

					<div class="shrink-0 text-right">
						<span class="font-semibold tabular-nums">
							{{ formatCurrency(account.balance) }}
						</span>
						<span class="ml-2 text-sm text-gray-500">
							{{ account.percentage.toFixed(1) }}%
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>