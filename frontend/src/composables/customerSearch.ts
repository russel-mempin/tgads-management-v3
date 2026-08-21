import { ref, watch, computed } from 'vue'
import type { Customer } from '@/types/customer'
import { getCustomerNames, getCustomerInfo } from '@/api/customers'

export function useCustomerSearch() {
  const customerNameToSearch = ref('')
  const showCustomerSuggestions = ref(false)
  const customerList = ref<string[]>([])
  const isNewCustomer = ref(false)
  const customerInfo = ref<Customer>({ name: '', contact_no: '', email: '', address: '', id: '' })
  const isLoadingList = ref(false)

  const loadCustomerList = async () => {
    isLoadingList.value = true
    try {
      customerList.value = await getCustomerNames()
    } finally {
      isLoadingList.value = false
    }
  }

  loadCustomerList()

  const filteredCustomers = computed(() => {
    if (!customerNameToSearch.value) return []
    const q = customerNameToSearch.value.toLowerCase()
    return customerList.value.filter((c) => c.toLowerCase().includes(q)).slice(0, 8)
  })
  const handleBlur = () => {
    setTimeout(() => {
      showCustomerSuggestions.value = false
    }, 150)
  }
  const selectCustomerToSearch = (name: string) => {
    customerNameToSearch.value = name
    showCustomerSuggestions.value = false
  }

  watch(customerNameToSearch, async (name) => {
    if (!name) {
      customerInfo.value = { name: '', contact_no: '', email: '', address: '', id: '' }
      return
    }
    const exists = customerList.value.some((c) => c.toLowerCase() === name.toLowerCase())
    if (exists) {
      isNewCustomer.value = false
      const data = await getCustomerInfo(name)
      if (!data) return
      customerInfo.value = {
        ...data,
        address: data.address?.trim() || 'N/A',
        contact_no: data.contact_no?.trim() || 'N/A',
        email: data.email?.trim() || 'N/A',
      }
    } else {
      isNewCustomer.value = true
      customerInfo.value = { name: name, contact_no: '', email: '', address: '' }
    }
  })

  return {
    customerNameToSearch,
    showCustomerSuggestions,
    customerList,
    isNewCustomer,
    customerInfo,
    filteredCustomers,
	isLoadingList,
    handleBlur,
    selectCustomerToSearch,
  }
}
