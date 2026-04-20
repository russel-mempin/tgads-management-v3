<script setup lang="ts">
import { computed, watch } from 'vue';
import type { JobItem } from '@/types/job_orders';
import type { ServiceType } from '@/types/services';
import { Button, Select, InputText, DataTable, Column, InputNumber } from 'primevue';
import { Plus, Trash } from '@lucide/vue'

const props = defineProps<{
	items: JobItem[],
	jo_number: number,
	service_list: ServiceType[]
}>()

const emit = defineEmits<{
	(e: 'update:items', value: JobItem[]): void
}>()

const localItems = computed({
	get: () => props.items,
	set: (value) => emit('update:items', value)
})

const addItemRow = () => {
	localItems.value = [
		...localItems.value,
		{
			jo_number: '',
			item_id: '',
			description: '',
			height: 0,
			width: 0,
			size_unit: '',
			paper_size: '',
			quantity: 0,
			job_status: '',
			due_date: '',
			discount: 0,
			unit_price: 0,
			subtotal: 0,
			total_claimed: 0,
			remaining_on_hand: 0,
			service_name: '',
			extra_service_name: '',
			extra_service_price: 0,
		}
	]
}

const removeItemRow = (index: number) => {
	const copy = [...localItems.value]
	copy.splice(index, 1)
	localItems.value = copy
}

const computeItemIds = (items: JobItem[]) => {
  // Track letter index per unique service name
  const serviceLetterMap = new Map<string, string>()
  const serviceCountMap = new Map<string, number>()
  let letterIndex = 0

  return items.map((item) => {
    if (!item.service_name) return item

    // Assign a letter to each unique service name
    if (!serviceLetterMap.has(item.service_name)) {
      serviceLetterMap.set(item.service_name, String.fromCharCode(65 + letterIndex))
      letterIndex++
    }

    const letter = serviceLetterMap.get(item.service_name)!
    const count = (serviceCountMap.get(item.service_name) ?? 0) + 1
    serviceCountMap.set(item.service_name, count)

    return {
      ...item,
      item_id: `${props.jo_number}${letter}${count}`
    }
  })
}

watch(localItems, (items) => {
  localItems.value = computeItemIds(items)
}, { deep: true })
</script>

<template>
	<DataTable :value="localItems" scrollable>
		<template #header>
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="text-xl font-medium text-slate-600">Job Items</span>
				<Button severity="contrast" @click="addItemRow">
					<Plus />
				</Button>
			</div>
		</template>
		<Column field="item_id" header="Item ID" />
		<Column header="Type">
			<template #body="{ data }">
			</template>
		</Column>
		<Column header="Description">
			<template #body="{ data }">
				<InputText v-model="data.description" placeholder="Description" />
			</template>
		</Column>
		<Column header="Qty.">
			<template #body="{ data }">
				<InputNumber v-model="data.quantity" placeholder="Qty." />
			</template>
		</Column>
		<Column header="Height">
			<template #body="{ data }">
				<InputNumber v-model="data.height" placeholder="Height" />
			</template>
		</Column>
		<Column header="Width">
			<template #body="{ data }">
				<InputNumber v-model="data.width" placeholder="Width" />
			</template>
		</Column>
		<Column header="Unit">
			<template #body="{ data }">
				<p>
					{{ service_list.find(data.service_name) }}
				</p>
			</template>
		</Column>
		<Column header="Paper Size">
			<template #body="{ data }">
				<InputText v-model="data.paper_size" placeholder="Paper Size" />
			</template>
		</Column>
		<Column header="Unit Price">
			<template #body="{ data }">
				<p>{{ data.unit_price }}</p>
			</template>
		</Column>
		<Column header="Due Date">
			<template #body="{ data }">
				<InputText v-model="data.paper_size" placeholder="Paper Size" />
			</template>
		</Column>
		<Column header="Job Status">
			<template #body="{ data }">
				<InputText v-model="data.paper_size" placeholder="Paper Size" />
			</template>
		</Column>
		<Column header="Extra Type">
			<template #body="{ data }">
				<InputText v-model="data.paper_size" placeholder="Paper Size" />
			</template>
		</Column>
		<Column header="Extra Price">
			<template #body="{ data }">
				<p>C</p>
			</template>
		</Column>
		<Column header="Discount"></Column>
		<Column header="Subtotal"></Column>
		<Column header="Claimed">
			<template #body="{ data }">
				<p>C</p>
			</template>
		</Column>
		<Column header="On Hand">
			<template #body="{ data }">
				<p>C</p>
			</template>
		</Column>
		<Column>
			<template #body="{ data, index }">
				<Button severity="danger" @click="removeItemRow(index)">
					<Trash />
				</Button>
			</template>
		</Column>
	</DataTable>
</template>