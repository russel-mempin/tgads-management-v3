import http from './http'

export const getMonthlyPerformanceList = async (year: number) => {
    const res = await http.get(`/performances/${year}`)
    return res.data
}

export const getMonthlyPerformance = async (year: number, month: number) => {
    const res = await http.get(`/performances/${year}/${month}`)
    return res.data
}