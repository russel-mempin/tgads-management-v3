<script setup lang="ts">
import { computed } from "vue";
import { formatDate, formatCurrency } from "@/utils/formatters";

const props = defineProps<{
  oldData: Record<string, unknown> | null;
  newData: Record<string, unknown> | null;
  entity: Record<string, unknown>;

  fieldOrder?: string[];
  fieldLabels?: Record<string, string>;
}>();

type ReviewField =
    | "date"
    | "account_name"
    | "description"
    | "reference_number"
    | "amount"
    | "is_archived";

const fields = computed<ReviewField[]>(() => props.fieldOrder as ReviewField[] ?? [
    "date",
    "account_name",
    "description",
    "reference_number",
    "amount",
    "is_archived",
]);

const labels = computed(() => ({
  date: "Date",
  account_name: "Method",
  description: "Description",
  reference_number: "Reference No.",
  amount: "Amount",
  is_archived: "Archived",
  ...props.fieldLabels,
}));

const diffRows = computed(() => {
  return fields.value.map((field) => {
    const changed = field in (props.oldData ?? {});

    return {
      field,
      label: labels.value[field] ?? field,
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

  if (field === "amount") {
    return formatCurrency(Number(value));
  }

  if (field === "date") {
    return formatDate(String(value));
  }

  if (field === "is_archived") {
    return value ? "Archived" : "Active";
  }

  return String(value);
}
</script>


<template>
  <div class="diff-table">
    <div class="diff-header">
      <span>Field</span>
      <span>{{ changedCount }} of {{ diffRows.length }} fields changed</span>
    </div>

    <div v-for="row in diffRows" :key="row.field" class="diff-row">
      <div class="diff-label" :class="{ changed: row.changed }">
        {{ row.label }}
      </div>

      <!-- Changed -->
      <div v-if="row.changed" class="diff-values">
        <div class="value old">
          {{ formatValue(row.field, row.oldV) }}
        </div>

        <div class="arrow">
          →
        </div>

        <div class="value new">
          {{ formatValue(row.field, row.newV) }}
        </div>
      </div>

      <!-- Unchanged -->
      <div v-else class="value unchanged">
        {{ formatValue(row.field, row.currentV) }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.diff-table {
  border: 1px solid #e4e1d8;
  border-radius: 6px;
  overflow: hidden;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #211f1b;
}

.diff-header {
  display: flex;
  justify-content: space-between;
  padding: 10px 16px;
  font-size: 12px;
  color: #5b5850;
  border-bottom: 1px solid #e4e1d8;
}

.diff-row {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #e4e1d8;
}

.diff-row:last-child {
  border-bottom: none;
}

.diff-label {
  width: 150px;
  min-width: 150px;
  padding: 12px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  color: #5b5850;
}

.diff-label.changed {
  color: #211f1b;
  font-weight: 600;
}

.diff-values {
  display: flex;
  align-items: stretch;
  flex: 1;
}

.value {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  font-variant-numeric: tabular-nums;
}

.value.old {
  background: #f8ece8;
  color: #9c4a34;
}

.value.new {
  background: #ebf2e9;
  color: #3c6b45;
  font-weight: 600;
}

.value.unchanged {
  flex: 1;
  color: #5b5850;
  padding: 12px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.unchanged-tag {
  font-size: 11px;
  color: #d2cec0;
  margin-left: 8px;
}

.arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  background: #f8ece8;
  color: #9c4a34;
}
</style>