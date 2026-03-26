import type { Job } from '../types'

interface Props {
  job: Job
  onClick: () => void
}

export function JobCard({ job, onClick }: Props) {
  const date = job.posted_at
    ? new Date(job.posted_at).toLocaleDateString('fi-FI', { day: 'numeric', month: 'short' })
    : null

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white rounded-2xl p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150 border border-greige-100 group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h2 className="font-semibold text-[#3a3530] text-base leading-snug group-hover:text-salmon-400 transition-colors truncate">
            {job.title}
          </h2>
          <p className="text-greige-400 text-sm mt-0.5 truncate">{job.company}</p>
        </div>
        <span className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full ${
          job.country === 'FI'
            ? 'bg-yellow-100 text-yellow-300' // intentionally dark text on yellow
            : 'bg-salmon-100 text-salmon-400'
        }`}
          style={job.country === 'FI' ? { color: '#b8860b' } : {}}
        >
          {job.country ?? 'INTL'}
        </span>
      </div>

      <div className="flex items-center gap-3 mt-3 text-xs text-greige-400">
        {job.location && (
          <span className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {job.location}
          </span>
        )}
        {job.salary_range && (
          <span className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {job.salary_range}
          </span>
        )}
        {date && <span className="ml-auto">{date}</span>}
      </div>

      {job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {job.tags.slice(0, 5).map(tag => (
            <span key={tag} className="text-xs bg-greige-50 text-greige-400 px-2 py-0.5 rounded-full border border-greige-100">
              {tag}
            </span>
          ))}
        </div>
      )}
    </button>
  )
}
