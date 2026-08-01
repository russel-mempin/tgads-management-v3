import http from './http'

export const getAccountOptions = async() => {
    const res = await http.get('/accounts/options')
    return res.data
}