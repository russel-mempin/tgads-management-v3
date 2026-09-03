import { defineStore } from 'pinia';
import { ref } from 'vue'
import { getAllServices, getAllExtras } from '@/api/services';
import { getAccountOptions } from '@/api/accounts';
import type { Service, Extra } from '@/types/service';
import type { AccountOption } from '@/types/account';

export const useReferenceStore = defineStore('reference', () => {
    const services = ref<Service[]>([])
    const extraServices = ref<Extra[]>([])
    const accountOptions = ref<AccountOption[]>([])
    const loaded = ref(false)

    const initialize = async () => {
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

    return {
        services,
        extraServices,
        accountOptions,
        initialize,
    }
})