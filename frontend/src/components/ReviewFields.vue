<script setup lang="ts">
import { computed } from "vue";
import { formatDate, formatCurrency } from "@/utils/formatters";

type FieldFormatter = "date" | "currency" | "boolean" | "text";

const props = withDefaults(
  defineProps<{
    oldData: Record<string, unknown> | null;
    newData: Record<string, unknown> | null;
    entity: Record<string, unknown>;

    fieldOrder: string[];
    fieldLabels?: Record<string, string>;
    fieldFormatters?: Record<string, FieldFormatter>;
  }>(),
  {
    fieldLabels: () => ({}),
    fieldFormatters: () => ({}),
  }
);

const diffRows = computed(() => {
  return props.fieldOrder.map((field) => {
    const changed = field in (props.oldData ?? {});

    return {
      field,
      label: props.fieldLabels[field] ?? field,
      oldV: props.oldData?.[field],
      newV: props.newData?.[field],
      currentV: props.entity?.[field],
      changed,
    };
  });
});

const changedCount = computed(() => {
  return diffRows.value.filter(row => row.changed).length;
});

function formatValue(field: string, value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const formatter = props.fieldFormatters[field] ?? "text";

  switch (formatter) {
    case "date":
      return formatDate(String(value));

    case "currency":
      return formatCurrency(Number(value));

    case "boolean":
      return value ? "Yes" : "No";

    default:
      return String(value);
  }
}

const columns = [
  {
    accessorKey: "label",
    header: "Field",
    id: "field",
  },
  {
    accessorKey: "value",
    header: "Value",
    id: "value",
  },
];
</script>

<template>
  <UTable :data="diffRows" :columns="columns" class="border border-default rounded-md">
    <template #field-cell="{ row }">
      <span :class="{ 'font-semibold': row.original.changed }">
        {{ row.original.label }}
      </span>
    </template>

    <template #value-cell="{ row }">
      <div v-if="row.original.changed" class="flex items-center gap-2">
        <span class="rounded bg-red-50 px-2 py-1 text-red-700">
          {{ formatValue(row.original.field, row.original.oldV) }}
        </span>

        <span>→</span>

        <span class="rounded bg-green-50 px-2 py-1 font-semibold text-green-700">
          {{ formatValue(row.original.field, row.original.newV) }}
        </span>
      </div>

      <span v-else class="text-muted">
        {{ formatValue(row.original.field, row.original.currentV) }}
      </span>
    </template>
  </UTable>

  <p class="mt-2 text-sm text-muted">
    {{ changedCount }} of {{ diffRows.length }} fields changed
  </p>
</template>