import { Link } from 'react-router-dom'
import { ArrowLeft, Server, Monitor, ChevronDown } from 'lucide-react'
import { RELEASES } from '../releaseNotes'

function ChangeList({ icon: Icon, title, items }) {
  if (!items?.length) return null
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        <Icon size={14} className="text-gray-400" />
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{title}</p>
      </div>
      <ul className="space-y-1.5 list-disc list-inside">
        {items.map((text, i) => (
          <li key={i} className="text-sm text-gray-600 leading-relaxed">{text}</li>
        ))}
      </ul>
    </div>
  )
}

export default function ReleaseNotesPage() {
  return (
    <div className="max-w-3xl space-y-5">
      <div>
        <Link to="/" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2">
          <ArrowLeft size={14} /> Back
        </Link>
        <h1 className="text-xl font-semibold text-gray-900">Release Notes</h1>
        <p className="text-xs text-gray-400 mt-0.5">Backend and frontend changes, by release.</p>
      </div>

      {RELEASES.length === 0 && (
        <p className="text-sm text-gray-400">No releases published yet.</p>
      )}

      <div className="space-y-3">
        {RELEASES.map((release, i) => (
          <details
            key={release.version}
            open={i === 0}
            className="group bg-white rounded-lg border border-gray-200"
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-5 py-4">
              <div className="flex items-baseline gap-2">
                <h2 className="text-base font-semibold text-gray-900 font-mono">{release.version}</h2>
                <span className="text-xs text-gray-400">{release.date}</span>
              </div>
              <ChevronDown size={16} className="text-gray-400 transition-transform group-open:rotate-180" />
            </summary>
            <div className="grid sm:grid-cols-2 gap-6 px-5 pb-5">
              <ChangeList icon={Server} title="Backend" items={release.backend} />
              <ChangeList icon={Monitor} title="Frontend" items={release.frontend} />
            </div>
          </details>
        ))}
      </div>
    </div>
  )
}
