import type { Job, JobFilters } from './types'

export async function fetchJobs(filters: JobFilters): Promise<Job[]> {
  const params = new URLSearchParams()
  if (filters.q)        params.set('q', filters.q)
  if (filters.company)  params.set('company', filters.company)
  if (filters.location) params.set('location', filters.location)
  if (filters.tag)      params.set('tag', filters.tag)
  if (filters.country)  params.set('country', filters.country)
  params.set('limit',  String(filters.limit))
  params.set('offset', String(filters.offset))

  const res = await fetch(`/jobs?${params}`)
  if (!res.ok) throw new Error(`Failed to fetch jobs: ${res.status}`)
  return res.json()
}

export async function fetchJob(id: number): Promise<Job> {
  const res = await fetch(`/jobs/${id}`)
  if (!res.ok) throw new Error(`Job not found: ${res.status}`)
  return res.json()
}
