import http from './http'

export const getCustomerNames = async() => {
    const res = await http.get('/customers/names')
    return res.data
}

export const getCustomerInfo = async(name: string) => {
    const res = await http.get(`/customers/${name}`)
    return res.data
}