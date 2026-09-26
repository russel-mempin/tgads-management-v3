import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAllServices } from '@/api/services'
import { getAllExtras } from '@/api/extras'
import { getAccountOptions } from '@/api/accounts'
import type { Service } from '@/types/service'
import type { Extra } from '@/types/extra'
import type { AccountOption } from '@/types/account'

export const useReferenceStore = defineStore('reference', () => {
    const services = ref<Service[]>([])
    const extraServices = ref<Extra[]>([])
    const accountOptions = ref<AccountOption[]>([])
    const loaded = ref(false)

    const refresh = async () => {
        const [servicesData, extrasData, accountsData] = await Promise.all([
            getAllServices(),
            getAllExtras(),
            getAccountOptions(),
        ])

        services.value = servicesData
        extraServices.value = extrasData
        accountOptions.value = accountsData
        loaded.value = true
    }

    const initialize = async () => {
        if (loaded.value) return

        await refresh()
    }

    return {
        services,
        extraServices,
        accountOptions,
        initialize,
        refresh,
    }
})