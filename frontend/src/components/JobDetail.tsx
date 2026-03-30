import type { Job } from '../types'

interface Props {
  job: Job
  onClose: () => void
}

export function JobDetail({ job, onClose }: Props) {
  const date = job.posted_at
    ? new Date(job.posted_at).toLocaleDateString('fi-FI', { day: 'numeric', month: 'long', year: 'numeric' })
    : null

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/20 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-white rounded-3xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white rounded-t-3xl px-6 pt-6 pb-4 border-b border-greige-100">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-xl font-semibold text-[#3a3530] leading-snug">{job.title}</h1>
              <p className="text-greige-400 mt-1">{job.company}</p>
            </div>
            <button
              onClick={onClose}
              className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-greige-100 hover:bg-greige-200 transition-colors text-greige-400"
            >
              ✕
            </button>
          </div>

          <div className="flex flex-wrap gap-2 mt-4">
            {job.country && (
              <span className="text-xs font-medium px-3 py-1 rounded-full bg-yellow-100"
                style={{ color: job.country === 'FI' ? '#b8860b' : undefined }}>
                {job.country}
              </span>
            )}
            {job.location && (
              <span className="text-xs px-3 py-1 rounded-full bg-greige-100 text-greige-400">
                📍 {job.location}
              </span>
            )}
            {job.salary_range && (
              <span className="text-xs px-3 py-1 rounded-full bg-salmon-100 text-salmon-400">
                {job.salary_range}
              </span>
            )}
            {date && (
              <span className="text-xs px-3 py-1 rounded-full bg-greige-100 text-greige-400">
                {date}
              </span>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          {job.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-5">
              {job.tags.map(tag => (
                <span key={tag} className="text-xs bg-greige-50 text-greige-400 px-2.5 py-1 rounded-full border border-greige-100">
                  {tag}
                </span>
              ))}
            </div>
          )}

          <div className="mb-5">
            {job.description ? (
              <p className="text-sm text-[#6b6560] leading-relaxed whitespace-pre-line">
                {job.description}
              </p>
            ) : (
              <div className="rounded-2xl border border-dashed border-greige-200 px-5 py-6 text-center">
                <p className="text-sm font-medium text-greige-400">We'd love to show you a description</p>
                <p className="text-xs text-greige-300 mt-1">but things are a bit sideways on that front. Head over to the listing for the full picture.</p>
              </div>
            )}
          </div>

          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center bg-salmon-300 hover:bg-salmon-400 text-white font-medium py-3 rounded-2xl transition-colors"
          >
            Apply →
          </a>
        </div>
      </div>
    </div>
  )
}
