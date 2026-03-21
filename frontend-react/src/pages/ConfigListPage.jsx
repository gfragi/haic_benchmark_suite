import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, AlertCircle, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

const STATUS = {
  completed: 'bg-green-100 text-green-800',
  running:   'bg-blue-100 text-blue-800',
  failed:    'bg-red-100 text-red-800',
  pending:   'bg-gray-100 text-gray-500',
}

function StatusBadge({ status }) {
  const s = status?.toLowerCase() ?? 'pending'
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize',
        STATUS[s] ?? STATUS.pending,
      )}
    >
      {s}
    </span>
  )
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function ConfigListPage() {
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 gap-2 text-gray-400 text-sm">
        <Loader2 size={16} className="animate-spin" />
        Loading configurations…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
        <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
        {error.message}
      </div>
    )
  }

  const configs = data ?? []

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Configurations</h1>
        <span className="text-xs text-gray-400 tabular-nums">
          {configs.length} {configs.length === 1 ? 'config' : 'configs'}
        </span>
      </div>

      {configs.length === 0 ? (
        <div className="text-center py-20 text-gray-400 text-sm">
          No configurations yet.
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-100">
            <thead>
              <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="px-4 py-3">Application</th>
                <th className="px-4 py-3">AI Model</th>
                <th className="px-4 py-3">Model Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Evaluation Date</th>
                <th className="px-4 py-3 w-24"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {configs.map((cfg) => (
                <tr
                  key={cfg.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/config/${cfg.id}/results`)}
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {cfg.application_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {cfg.ai_model_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                    {cfg.ai_model_type}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={cfg.evaluation_status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 tabular-nums">
                    {formatDate(cfg.evaluation_date)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/config/${cfg.id}/results`)
                      }}
                      className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      View results
                      <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
