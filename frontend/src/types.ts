export interface Job {
  id: number
  title: string
  company: string
  location: string | null
  url: string
  tags: string[]
  salary_range: string | null
  posted_at: string | null
  scraped_at: string
  country: string | null
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
