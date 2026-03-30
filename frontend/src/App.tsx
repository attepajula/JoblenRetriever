import { useState, useEffect, useCallback } from 'react'
import { fetchJobs } from './api'
import { JobCard } from './components/JobCard'
import { JobDetail } from './components/JobDetail'
import type { Job, JobFilters } from './types'

const PAGE_SIZE = 20

function CardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-5 animate-pulse border border-greige-100">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-greige-100 rounded-full w-3/4" />
          <div className="h-3 bg-greige-100 rounded-full w-2/5" />
        </div>
        <div className="h-5 w-10 bg-greige-100 rounded-full shrink-0" />
      </div>
      <div className="h-3 bg-greige-100 rounded-full w-full mb-1.5" />
      <div className="h-3 bg-greige-100 rounded-full w-4/5 mb-4" />
      <div className="flex items-center gap-3">
        <div className="h-3 bg-greige-100 rounded-full w-24" />
        <div className="h-3 bg-greige-100 rounded-full w-16 ml-auto" />
      </div>
    </div>
  )
}

function EmptyState({ q }: { q: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center px-4">
      <div className="text-5xl mb-4 select-none">¯\_(ツ)_/¯</div>
      <h2 className="text-lg font-semibold text-[#3a3530] mb-2">
        {q ? `Nothing for "${q}"` : 'No jobs found'}
      </h2>
      <p className="text-sm text-greige-400 max-w-xs">
        {q
          ? "The robots searched high and low and came back empty-handed. Try different keywords."
          : "Looks like the job market took a day off. Try adjusting your filters."}
      </p>
    </div>
  )
}

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<Job | null>(null)

  const [q, setQ] = useState('')
  const [country, setCountry] = useState<'' | 'FI' | 'INTL'>('')
  const [page, setPage] = useState(0)

  const load = useCallback(async (filters: JobFilters) => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchJobs(filters)
      setJobs(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const t = setTimeout(() => {
      load({ q, country: country || undefined, limit: PAGE_SIZE, offset: page * PAGE_SIZE })
    }, 300)
    return () => clearTimeout(t)
  }, [q, country, page, load])

  const totalPages = total !== null ? Math.ceil(total / PAGE_SIZE) : null

  return (
    <div className="min-h-screen bg-greige-50">
      {/* Header */}
      <header className="bg-white border-b border-greige-100 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-3 flex flex-col sm:flex-row sm:items-center gap-3">
          <h1 className="text-xl font-bold text-[#3a3530] tracking-tight shrink-0">
            Joblen<span className="text-salmon-300">.</span>
          </h1>

          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* Search */}
            <div className="flex-1 min-w-0 relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-greige-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search jobs..."
                value={q}
                onChange={e => { setQ(e.target.value); setPage(0) }}
                className="w-full pl-9 pr-4 py-2 rounded-xl border border-greige-200 bg-greige-50 text-sm focus:outline-none focus:ring-2 focus:ring-salmon-200 placeholder:text-greige-300"
              />
            </div>

            {/* Country filter */}
            <div className="flex rounded-xl border border-greige-200 overflow-hidden text-sm shrink-0">
              {(['', 'FI', 'INTL'] as const).map(c => (
                <button
                  key={c}
                  onClick={() => { setCountry(c); setPage(0) }}
                  className={`px-3 py-2 transition-colors ${
                    country === c
                      ? 'bg-salmon-200 text-[#3a3530] font-medium'
                      : 'bg-white text-greige-400 hover:bg-greige-50'
                  }`}
                >
                  {c === '' ? 'All' : c}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        {error && (
          <div className="mb-4 px-4 py-3 bg-salmon-100 text-salmon-400 rounded-xl text-sm">
            {error}
          </div>
        )}

        {/* Result count */}
        {!loading && total !== null && total > 0 && (
          <p className="text-xs text-greige-400 mb-3">
            {total.toLocaleString()} job{total !== 1 ? 's' : ''}
            {q && <span> for <span className="text-[#3a3530] font-medium">"{q}"</span></span>}
            {totalPages && totalPages > 1 && <span> — page {page + 1} of {totalPages}</span>}
          </p>
        )}

        {loading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)}
          </div>
        ) : jobs.length === 0 ? (
          <EmptyState q={q} />
        ) : (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              {jobs.map(job => (
                <JobCard key={job.id} job={job} onClick={() => setSelected(job)} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages !== null && totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 rounded-xl bg-white border border-greige-200 text-sm text-greige-400 disabled:opacity-40 hover:bg-greige-50 transition-colors"
                >
                  ← Prev
                </button>
                <span className="text-sm text-greige-400">
                  {page + 1} / {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page + 1 >= totalPages}
                  className="px-4 py-2 rounded-xl bg-white border border-greige-200 text-sm text-greige-400 disabled:opacity-40 hover:bg-greige-50 transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {selected && <JobDetail job={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
