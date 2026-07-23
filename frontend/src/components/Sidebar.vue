<script setup lang="ts">
import { ref, computed } from 'vue'
import { useColorMode } from '@vueuse/core'
import type { DropdownMenuItem, NavigationMenuItem } from '@nuxt/ui'
import { useAuthStore } from '@/stores/auth'
import logo from '@/assets/Logo.png'

const open = defineModel<boolean>('open', { default: true })
const colorMode = useColorMode()
const authStore = useAuthStore()

type NavItem = NavigationMenuItem & {
  category: string
  adminOnly?: boolean
  ownerOnly?: boolean
  superuserOnly?: boolean
}

const allItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: 'i-lucide-layout-dashboard', category: 'None' },
  { to: '/job-orders', label: 'Job Orders', icon: 'i-lucide-briefcase-business', category: 'Operations' },
  { to: '/review-data', label: 'Needs Review', icon: 'i-lucide-scan-eye', category: 'Operations', ownerOnly: true },
  { to: '/job-orders/voided', label: 'Voided Jobs', icon: 'i-lucide-printer-x', category: 'Operations', ownerOnly: true },
  // { to: '/customers', label: 'Customers', icon: 'i-lucide-book-user', category: 'Operations' },
  // { to: '/sales', label: authStore.isOwner ? 'Sales' : 'Daily Sales', icon: 'i-lucide-banknote-arrow-up', category: 'Finance' },
  // { to: '/expenses', label: authStore.isOwner ? 'Expenses' : 'Daily Expenses', icon: 'i-lucide-banknote-arrow-down', category: 'Finance' },
  // { to: '/deposits', label: 'Deposits', icon: 'i-lucide-landmark', category: 'Finance', adminOnly: true },
  // { to: '/reports/daily', label: 'Daily Collection', icon: 'i-lucide-sheet', category: 'Reports', ownerOnly: true },
  // { to: '/reports/monthly', label: 'Monthly Performance', icon: 'i-lucide-sheet', category: 'Reports', ownerOnly: true },
  // { to: '/manage-services', label: 'Manage Services', icon: 'i-lucide-concierge-bell', category: 'Settings', adminOnly: true },
  // { to: '/manage-extras', label: 'Manage Extras', icon: 'i-lucide-layers', category: 'Settings', adminOnly: true },
  // { to: '/manage-users', label: 'Manage Users', icon: 'i-lucide-user-cog', category: 'Settings', adminOnly: true },
  // { to: '/audit-logs', label: 'Audit Logs', icon: 'i-lucide-activity', category: 'Settings', superuserOnly: true }
]

const visibleItems = computed(() => allItems.filter(item => {
  if (item.superuserOnly) return authStore.isSuperuser
  if (item.ownerOnly) return authStore.isOwner
  if (item.adminOnly) return authStore.isAdmin
  return true
}))

// 'None' has no heading; the rest render as "OPERATIONS", "FINANCE", etc.
const categoryOrder = ['None', 'Operations', 'Finance', 'Reports', 'Settings']

const navGroups = computed(() =>
  categoryOrder
    .map(category => ({
      category,
      items: visibleItems.value.filter(item => item.category === category)
    }))
    .filter(group => group.items.length > 0)
)

const user = computed(() => {
  const u = authStore.user
  const fullName = u ? `${u.first_name} ${u.last_name}` : 'Guest'
  return {
    name: fullName,
    avatar: { alt: fullName }
  }
})

const userItems = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: 'Light Mode',
      icon: 'i-lucide-sun',
      type: 'checkbox',
      checked: colorMode.value === 'light',
      onUpdateChecked(checked: boolean) {
        if (checked) colorMode.value = 'light'
      },
      onSelect(e: Event) { e.preventDefault() }
    },
    {
      label: 'Dark Mode',
      icon: 'i-lucide-moon',
      type: 'checkbox',
      checked: colorMode.value === 'dark',
      onUpdateChecked(checked: boolean) {
        if (checked) colorMode.value = 'dark'
      },
      onSelect(e: Event) { e.preventDefault() }
    },
    {
      label: 'Log out',
      icon: 'i-lucide-log-out',
      onSelect() { authStore.logout() }
    }
  ]
])
</script>

<template>
  <USidebar v-model:open="open" collapsible="icon" rail :ui="{
    container: 'h-full',
    inner: 'bg-elevated/25 divide-transparent',
    body: 'py-0 px-1.5 bg-default/75 backdrop-blur-md'
  }">
    <template #header="{ state }">
      <div class="flex items-center gap-2 px-1.5 py-1 w-full"
        :class="state === 'collapsed' ? 'justify-center px-0' : ''">
        <div class="flex items-center justify-center size-8 shrink-0">
          <img :src="logo" alt="Team Graphics ADS" class="size-8 object-contain" />
        </div>
        <div v-if="state === 'expanded'" class="flex flex-col overflow-hidden">
          <span class="font-montserrat font-semibold text-highlighted truncate">Team Graphics ADS</span>
          <span class="font-montserrat tracking-wide text-xs text-muted truncate">Management System</span>
        </div>
      </div>
    </template>

    <template #default="{ state }">
      <div class="flex flex-col gap-1">
        <template v-for="group in navGroups" :key="group.category">
          <p v-if="group.category !== 'None' && state === 'expanded'"
            class="font-montserrat px-2.5 mt-3 mb-1 text-xs font-semibold tracking-wider text-muted uppercase truncate">
            {{ group.category }}
          </p>
          <UNavigationMenu :items="group.items" orientation="vertical" :collapsed="state === 'collapsed'" tooltip :ui="{
            link: state === 'collapsed'
              ? 'justify-center px-0 py-3 overflow-hidden'
              : 'px-4 py-3 overflow-hidden gap-4'
          }" />
        </template>
      </div>
    </template>

    <template #footer>
      <UDropdownMenu :items="userItems" :content="{ align: 'center', collisionPadding: 12 }"
        :ui="{ content: 'w-(--reka-dropdown-menu-trigger-width) min-w-48' }">
        <UButton v-bind="user" :label="user?.name" trailing-icon="i-lucide-chevrons-up-down" color="neutral"
          variant="subtle" square class="w-full data-[state=open]:bg-elevated overflow-hidden" :ui="{
            trailingIcon: 'text-dimmed ms-auto'
          }" />
      </UDropdownMenu>
    </template>
  </USidebar>
</template>