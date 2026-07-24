export interface VoidedJobs {
    id: string
    jo_number: number
    job_date: Date
    voided_at: Date
    reason: string
    voided_by_name: string
}