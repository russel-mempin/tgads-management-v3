<script setup lang="ts">
import type { Customer } from '@/types/customer'

const props = defineProps<{
  isWalkIn: boolean
  hasJobItems: boolean
  customerList: string[]
  isNewCustomer: boolean
  filteredCustomers: string[]
  handleBlur: () => void
  selectCustomerToSearch: (name: string) => void
}>()

const customerNameToSearch = defineModel<string>('customerNameToSearch', { required: true })
const showCustomerSuggestions = defineModel<boolean>('showCustomerSuggestions', { required: true })
const customerInfo = defineModel<Customer>('customerInfo', { required: true })
</script>

<template>
	<Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2"
		enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
		leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
		<div v-if="!isWalkIn" class="bg-default border border-default rounded-md p-6 m-8">
			<div class="flex items-center gap-2 mb-8">
				<UIcon name="i-lucide-user" class="bg-primary w-6 h-6 rounded-md p-1 text-inverted shrink-0" />
				<h2 class="font-semibold text-highlighted">Customer</h2>
			</div>
			<UFormField label="Name" hint="Type to search existing customers, or enter a new name." required>
				<div class="relative">
					<UInput v-model="customerNameToSearch" placeholder="Search or enter customer name" size="lg"
						class="w-full" @focus="showCustomerSuggestions = true" @blur="handleBlur" />
					<div v-if="showCustomerSuggestions && filteredCustomers.length"
						class="absolute z-20 mt-1 w-full bg-default border border-default rounded-md shadow-lg max-h-48 overflow-y-auto">
						<button v-for="name in filteredCustomers" :key="name" type="button"
							class="w-full text-left px-3 py-2 hover:bg-elevated text-sm"
							@mousedown="selectCustomerToSearch(name)">
							{{ name }}
						</button>
					</div>
				</div>
			</UFormField>
			<div class="mt-6 grid grid-cols-3 gap-6">
				<UFormField label="Contact Number">
					<UInput v-model="customerInfo.contact_no" placeholder="09XX-XXX-XXXX" size="lg" class="w-full"
						:disabled="!isNewCustomer" />
				</UFormField>
				<UFormField label="Email">
					<UInput v-model="customerInfo.email" placeholder="teamgraphicads@yahoo.com" size="lg" class="w-full"
						:disabled="!isNewCustomer"
						:hint="hasJobItems ? 'Existing info not editable here.' : ''" />
				</UFormField>
				<UFormField label="Address">
					<UInput v-model="customerInfo.address" :items="customerList" placeholder="134 Luzon Ave." size="lg"
						class="w-full" :disabled="!isNewCustomer"
						:hint="hasJobItems ? 'Existing info not editable here.' : ''" />
				</UFormField>
			</div>
		</div>
	</Transition>
</template>