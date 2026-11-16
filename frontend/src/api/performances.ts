import http from './http'

export const getMonthlyPerformanceList = async (year: string) => {
    const res = await http.get('/performances/', {
        params: { year }
    })
    return res.data
}