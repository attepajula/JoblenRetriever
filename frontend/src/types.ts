export interface Job {
  id: number
  title: string
  company: string
  location: string | null
  url: string
  description: string | null
  tags: string[]
  salary_range: string | null
  posted_at: string | null
  scraped_at: string
  country: string | null
}

export interface JobsResponse {
  items: Job[]
  total: number
}

export interface JobFilters {
  q?: string
  company?: string
  location?: string
  tag?: string
  country?: string
  limit: number
  offset: number
}
