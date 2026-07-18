<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { JobOrder } from '@/types/job_ordersTypes'
import { getJobOrder } from '@/api/job_orders'
import { formatDate, formatCurrency, nowInManila } from '@/utils/formatters'

const route = useRoute()
const jobOrder = ref<JobOrder>()

onMounted(async () => {
	jobOrder.value = await getJobOrder(Number(route.params.jo_number))
	await nextTick()
	window.print()
})

const MIN_JOB_ITEM_ROWS = 5
const MIN_PAYMENT_ROWS = 3
const MIN_CLAIM_ROWS = 3

const paddedJobItems = computed(() => {
	const items = jobOrder.value?.job_items ?? []
	const blanksNeeded = Math.max(0, MIN_JOB_ITEM_ROWS - items.length)
	return [...items, ...Array(blanksNeeded).fill(null)]
})

const paddedPayments = computed(() => {
	const payments = jobOrder.value?.payments ?? []
	const blanksNeeded = Math.max(0, MIN_PAYMENT_ROWS - payments.length)
	return [...payments, ...Array(blanksNeeded).fill(null)]
})

const paddedClaims = computed(() => {
	const claims = jobOrder.value?.claims ?? []
	const blanksNeeded = Math.max(0, MIN_CLAIM_ROWS - claims.length)
	return [...claims, ...Array(blanksNeeded).fill(null)]
})
</script>

<template>
	<button class="print-btn no-print" onclick="window.print()">⎙ PRINT FORM</button>

	<div class="page">

		<!-- HEADER -->
		<div class="header">
			<div class="brand">
				<div class="brand-icon">
					<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
						<path d="M3 3h18v4H3zM3 9h12v2H3zM3 13h12v2H3zM3 17h8v2H3zM17 12l5 8h-3v3h-4v-3h-3z" />
					</svg>
					<span class="brand-name">TEAM GRAPHICS ADS</span>
				</div>
			</div>
			<div class="form-title-block">
				<div class="form-subtitle">Monitoring Form</div>
			</div>
		</div>

		<!-- METADATA -->
		<div class="meta-bar">
			<div class="meta-field">
				<div class="meta-label">JO Number</div>
				<div class="meta-value">{{ jobOrder?.jo_number }}</div>
			</div>
			<div class="meta-field">
				<div class="meta-label">Date Received</div>
				<div class="meta-value">{{ formatDate(jobOrder?.date_received) }}</div>
			</div>
			<div class="meta-field">
				<div class="meta-label">Payment Status</div>
				<div class="meta-value">{{ jobOrder?.payment_status }}</div>
			</div>
			<div class="meta-field">
				<div class="meta-label">Print Date / Time</div>
				<div class="meta-value">{{ formatDate(nowInManila()) }}</div>
			</div>
		</div>

		<!-- SECTION 1: CUSTOMER INFO -->
		<div class="section">
			<div class="section-header">
				<div class="section-num">1</div>
				<div class="section-title">Customer Information</div>
				<div class="section-rule"></div>
			</div>
			<div class="flex flex-col gap-4">
				<div class="outer-border">
					<div class="field-row" style="grid-template-columns: 1fr;">
						<div class="field">
							<div class="field-label">Full Name / Company Name</div>
							<div class="field-value">{{ jobOrder?.customer_name }}</div>
						</div>
					</div>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div class="outer-border">
						<div class="field-row" style="grid-template-columns: 1fr;">
							<div class="field">
								<div class="field-label">Contact No</div>
								<div class="field-value">{{ jobOrder?.customer_contact_no }}</div>
							</div>
						</div>
					</div>
					<div class="outer-border">
						<div class="field-row" style="grid-template-columns: 1fr;">
							<div class="field">
								<div class="field-label">Email Address</div>
								<div class="field-value">{{ jobOrder?.customer_email }}</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- SECTION 2: JOB ITEMS -->
		<div class="section">
			<div class="section-header">
				<div class="section-num">2</div>
				<div class="section-title">Job Item Information</div>
				<div class="section-rule"></div>
			</div>
			<table class="job-table">
				<thead>
					<tr>
						<th class="col-item_id">Item ID</th>
						<th class="col-service">Service / Description</th>
						<th class="col-qty">Qty</th>
						<th class="col-pcs">Dimensions</th>
						<th class="col-price">Price (₱)</th>
						<th class="col-done">Fulfilled?</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(item, index) in paddedJobItems" :key="item?.item_id ?? `blank-${index}`">
						<td>{{ item?.item_id ?? '' }}</td>
						<td>{{ item ? `${item.service_name} – ${item.description}` : '' }}</td>
						<td>{{ item?.quantity ?? '' }}</td>
						<td>{{ item ? `${item.width} × ${item.height} ${item.size_unit}` : '' }}</td>
						<td>{{ item ? formatCurrency(item.subtotal) : '' }}</td>
						<td>
							<div class="checkbox-row" v-if="item">
								<span class="cb" style="background:#0f0f0f;"></span>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- PAYMENT -->
		<div class="section">
			<div class="section-header">
				<div class="section-num">3</div>
				<div class="section-title">Payment Information</div>
				<div class="section-rule"></div>
			</div>
			<table class="pay-table" style="margin-top: 3mm;">
				<thead>
					<tr>
						<th class="col-amount">Amount (₱)</th>
						<th class="col-date">Date Received</th>
						<th class="col-method">Method</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(payment, index) in paddedPayments" :key="payment?.date_received ?? `blank-${index}`">
						<td>{{ payment ? formatCurrency(payment.amount) : '' }}</td>
						<td>{{ payment ? formatDate(payment.date_received) : '' }}</td>
						<td>{{ payment?.method ?? '' }}</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- CLAIMING HISTORY -->
		<div class="section">
			<div class="section-header">
				<div class="section-num">4</div>
				<div class="section-title">Claiming History</div>
				<div class="section-rule"></div>
			</div>
			<table class="claim-table">
				<thead>
					<tr>
						<th style="width:24%">Date</th>
						<th style="width:26%">Name</th>
						<th style="width:28%">Item Claimed</th>
						<th style="width:22%">Pcs.</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(claim, index) in paddedClaims" :key="claim?.date_claimed ?? `blank-${index}`">
						<td>{{ claim ? formatDate(claim.date_claimed) : '' }}</td>
						<td>{{ claim?.name ?? '' }}</td>
						<td>{{ claim?.claimed_item_id ?? '' }}</td>
						<td>{{ claim?.pcs_claimed ?? '' }}</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- FOOTER -->
		<div class="form-footer">
			<div class="footer-note uppercase">Handwritten entries are temporary — update the system once available.
			</div>
			<div class="footer-copy">Form Rev. 01</div>
		</div>

	</div>
</template>

<style scoped>
*,
*::before,
*::after {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

:root {
	--ink: #0f0f0f;
	--mid: #5a5a5a;
	--light: #c8c8c8;
	--rule: #d0d0d0;
	--accent: #e8380d;
	--paper: #ffffff;
}

body {
	background: #e0ddd8;
	font-family: 'DM Sans', sans-serif;
	padding: 40px 20px;
	min-height: 100vh;
	display: flex;
	justify-content: center;
	align-items: flex-start;
}

.page {
	width: 210mm;
	height: 297mm;
	overflow: hidden;
	background: var(--paper);
	box-shadow: 0 8px 40px rgba(0, 0, 0, 0.18), 0 2px 8px rgba(0, 0, 0, 0.08);
	padding: 14mm;
	position: relative;
	overflow: hidden;
	font-family: 'DM Sans', sans-serif;
	margin: 40px auto;
}

.page::before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	width: 6px;
	background: #e8380d;
}

.page::after {
	content: 'JOB ORDER';
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%) rotate(-35deg);
	font-size: 90px;
	color: rgba(0, 0, 0, 0.03);
	letter-spacing: 12px;
	pointer-events: none;
	white-space: nowrap;
	user-select: none;
}

.header {
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
	margin-bottom: 8mm;
	padding-bottom: 4mm;
	border-bottom: 2px solid #0f0f0f;
}

.brand {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.brand-icon {
	display: flex;
	align-items: center;
	gap: 8px;
}

.brand-icon svg {
	width: 28px;
	height: 28px;
	fill: #e8380d;
}

.brand-name {
	font-size: 28px;
	letter-spacing: 3px;
	color: #0f0f0f;
	line-height: 1;
	font-weight: 700;
}

.brand-sub {
	font-size: 9px;
	letter-spacing: 3px;
	text-transform: uppercase;
	color: #5a5a5a;
	font-weight: 500;
	margin-left: 36px;
}

.form-title-block {
	text-align: right;
}

.form-title {
	font-size: 34px;
	letter-spacing: 4px;
	color: #0f0f0f;
	line-height: 1;
	font-weight: 700;
}

.form-subtitle {
	font-size: 8px;
	letter-spacing: 2.5px;
	text-transform: uppercase;
	color: #5a5a5a;
	font-weight: 500;
}

.meta-bar {
	display: grid;
	grid-template-columns: 1fr 1.2fr 1fr 1.2fr;
	gap: 4mm;
	margin-bottom: 5mm;
	background: #0f0f0f;
	padding: 4mm 5mm;
}

.meta-field {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.meta-label {
	font-size: 7.5px;
	letter-spacing: 2px;
	text-transform: uppercase;
	color: #e8380d;
	font-family: monospace;
}

.meta-value {
	color: white;
	font-family: monospace;
	font-size: 12px;
	margin-top: 2px;
}

.section {
	margin-bottom: 4.5mm;
}

.section-header {
	display: flex;
	align-items: center;
	gap: 6px;
	margin-bottom: 1mm;
}

.section-num {
	font-size: 11px;
	color: white;
	background: #e8380d;
	width: 18px;
	height: 18px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	font-weight: 700;
}

.section-title {
	font-size: 13px;
	color: #0f0f0f;
	font-weight: 700;
	font-family: Montserrat;
}

.section-rule {
	flex: 1;
	height: 1px;
	background: #d0d0d0;
}

.field-row {
	display: grid;
	border-bottom: 1px solid #d0d0d0;
}

.field-row:last-child {
	border-bottom: none;
}

.field {
	padding: 2.5mm 3mm;
	border-right: 1px solid #d0d0d0;
	min-height: 10mm;
	display: flex;
	flex-direction: column;
	justify-content: flex-end;
	gap: 2px;
}

.field:last-child {
	border-right: none;
}

.field-label {
	font-size: 6.5px;
	letter-spacing: 1.8px;
	text-transform: uppercase;
	color: #5a5a5a;
	line-height: 1;
	font-family: monospace;
}

.field-value {
	font-size: 11px;
	color: #0f0f0f;
	padding-top: 2px;
	border-bottom: 1.5px solid #0f0f0f;
	min-height: 5mm;
}

.job-table {
	width: 100%;
	border-collapse: collapse;
}

.job-table th {
	font-size: 7px;
	letter-spacing: 1.5px;
	text-transform: uppercase;
	color: white;
	background: #0f0f0f;
	padding: 2.5mm 3mm;
	text-align: left;
	border-right: 1px solid rgba(255, 255, 255, 0.15);
	font-weight: 500;
	font-family: monospace;
}

.job-table th:last-child {
	border-right: none;
}

.job-table td {
	border-bottom: 1px solid #d0d0d0;
	border-right: 1px solid #d0d0d0;
	height: 9mm;
	padding: 0 3mm;
	vertical-align: middle;
	font-size: 9px;
}

.job-table td:last-child {
	border-right: none;
}

.col_item_id {
	width: 35%;
}

.col-service {
	width: 35%;
}

.col-qty {
	width: 10%;
}

.col-pcs {
	width: 5%;
}

.col-price {
	width: 10%;
}

.col-done {
	width: 5%;
}

.checkbox-row {
	display: flex;
	align-items: center;
	gap: 4px;
}

.cb {
	width: 9px;
	height: 9px;
	border: 1.5px solid #0f0f0f;
	display: inline-block;
	flex-shrink: 0;
}

.cb-label {
	font-family: monospace;
	font-size: 7px;
	color: #5a5a5a;
	letter-spacing: 0.5px;
}

.bottom-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 5mm;
}

.summary-row {
	display: flex;
	justify-content: space-between;
	padding: 1mm 2mm;
	border-bottom: 1px solid #d0d0d0;
	font-size: 9px;
}

.summary-label {
	color: #5a5a5a;
	font-family: monospace;
	text-transform: uppercase;
	letter-spacing: 1px;
	font-size: 7px;
}

.summary-value {
	font-weight: 600;
	color: #0f0f0f;
}

.pay-table {
	width: 100%;
	border-collapse: collapse;
}

.pay-table th {
	font-size: 7px;
	letter-spacing: 1.5px;
	text-transform: uppercase;
	color: white;
	background: #0f0f0f;
	padding: 2.5mm 3mm;
	text-align: left;
	border-right: 1px solid rgba(255, 255, 255, 0.15);
	font-weight: 500;
	font-family: monospace;
}

.pay-table th:last-child {
	border-right: none;
}

.pay-table td {
	border-bottom: 1px solid #d0d0d0;
	border-right: 1px solid #d0d0d0;
	height: 9mm;
	padding: 0 2.5mm;
	vertical-align: middle;
	font-size: 9px;
}

.pay-table td:last-child {
	border-right: none;
}

.col-amount {
	width: 30%;
}

.col-date {
	width: 32%;
}

.col-method {
	width: 38%;
}

.claim-table {
	width: 100%;
	border-collapse: collapse;
}

.claim-table th {
	font-size: 6.5px;
	letter-spacing: 1.2px;
	text-transform: uppercase;
	color: white;
	background: #0f0f0f;
	padding: 2mm 2.5mm;
	text-align: left;
	border-right: 1px solid rgba(255, 255, 255, 0.15);
	font-weight: 500;
	font-family: monospace;
}

.claim-table th:last-child {
	border-right: none;
}

.claim-table td {
	border-bottom: 1px solid #d0d0d0;
	border-right: 1px solid #d0d0d0;
	height: 8.5mm;
	padding: 0 2.5mm;
	font-size: 9px;
	vertical-align: middle;
}

.claim-table td:last-child {
	border-right: none;
}

.form-footer {
	margin-top: 5mm;
	padding-top: 3mm;
	border-top: 1px solid #d0d0d0;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.footer-note {
	font-size: 12px;
	color: #c8c8c8;
	letter-spacing: 1px;
	font-family: monospace;
}

.footer-copy {
	font-size: 7px;
	color: #c8c8c8;
	letter-spacing: 0.5px;
}

.outer-border {
	border: 1px solid #d0d0d0;
}

.print-btn {
	position: fixed;
	bottom: 28px;
	right: 28px;
	background: #e8380d;
	color: white;
	border: none;
	padding: 12px 22px;
	font-size: 16px;
	letter-spacing: 3px;
	cursor: pointer;
	box-shadow: 0 4px 20px rgba(232, 56, 13, 0.4);
	transition: transform 0.1s, box-shadow 0.1s;
	z-index: 100;
	font-weight: 700;
}

.print-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 24px rgba(232, 56, 13, 0.5);
}

@media print {
	* {
		print-color-adjust: exact;
		-webkit-print-color-adjust: exact;
	}

	body {
		background: none;
		padding: 0;
	}

	.page {
		box-shadow: none;
		width: 210mm;
		height: 297mm;
		margin: 0;
	}

	.no-print {
		display: none !important;
	}

	@page {
		size: 210mm 297mm;
		margin: 0;
	}
}
</style>