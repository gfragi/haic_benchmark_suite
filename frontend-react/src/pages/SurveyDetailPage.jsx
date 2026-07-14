import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer, CartesianGrid,
} from 'recharts'
import { ArrowLeft, Loader2, ChevronDown } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import { SUS_QUESTIONS, ETHICS_QUESTIONS } from '../surveyConfig'

function VersionBarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded shadow-sm text-xs p-2">
      <p className="font-semibold text-gray-800 mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.fill }}>
          {p.name}: {p.value?.toFixed(1)}
        </p>
      ))}
    </div>
  )
}

function QuestionExplainer({ title, questions }) {
  return (
    <details className="group rounded-lg border border-gray-200 bg-white">
      <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 text-sm font-medium text-gray-700">
        {title}
        <ChevronDown size={14} className="text-gray-400 transition-transform group-open:rotate-180" />
      </summary>
      <ol className="space-y-1.5 px-4 pb-4 text-xs text-gray-500 list-decimal list-inside">
        {questions.map((q) => (
          <li key={q.key}>{q.text}</li>
        ))}
      </ol>
    </details>
  )
}

function scoreCellClass(value) {
  if (value == null) return 'bg-gray-50 text-gray-300'
  if (value >= 4) return 'bg-green-100 text-green-800'
  if (value >= 3) return 'bg-amber-50 text-amber-700'
  return 'bg-red-50 text-red-700'
}

function QuestionCompareTable({ title, questions, avgA, avgB, versionA, versionB }) {
  return (
    <div>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{title}</p>
      <div className="overflow-hidden rounded-md border border-gray-200">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="bg-gray-50 text-left text-gray-500">
              <th className="px-3 py-2 font-medium">Question</th>
              <th className="px-3 py-2 font-medium text-center">{versionA}</th>
              <th className="px-3 py-2 font-medium text-center">{versionB}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {questions.map((q) => {
              const a = avgA?.[q.key]
              const b = avgB?.[q.key]
              return (
                <tr key={q.key}>
                  <td className="px-3 py-2 text-gray-600">{q.text}</td>
                  <td className={clsx('px-3 py-2 text-center font-mono', scoreCellClass(a))}>
                    {a == null ? '—' : Number(a).toFixed(2)}
                  </td>
                  <td className={clsx('px-3 py-2 text-center font-mono', scoreCellClass(b))}>
                    {b == null ? '—' : Number(b).toFixed(2)}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function SurveyDetailPage() {
  const { id: configId } = useParams()
  const [versionA, setVersionA] = useState('')
  const [versionB, setVersionB] = useState('')

  const { data: config } = useQuery({
    queryKey: ['config', configId],
    queryFn: () => api.configs.get(configId),
  })

  const pilotTag = config?.pilot_tag || null

  const { data: aggregate, isLoading: aggregateLoading } = useQuery({
    queryKey: ['survey-aggregate', pilotTag],
    queryFn: () => api.survey.aggregate(pilotTag),
    enabled: !!pilotTag,
  })

  const { data: versions } = useQuery({
    queryKey: ['survey-versions', pilotTag],
    queryFn: () => api.survey.versions(pilotTag),
    enabled: !!pilotTag,
  })

  const canCompare = !!versionA && !!versionB && versionA !== versionB

  const { data: compareData } = useQuery({
    queryKey: ['survey-compare', pilotTag, versionA, versionB],
    queryFn: () => api.survey.compare(pilotTag, versionA, versionB),
    enabled: canCompare,
  })

  const { data: qaA } = useQuery({
    queryKey: ['survey-question-averages', pilotTag, versionA],
    queryFn: () => api.survey.questionAverages(pilotTag, versionA),
    enabled: canCompare,
  })

  const { data: qaB } = useQuery({
    queryKey: ['survey-question-averages', pilotTag, versionB],
    queryFn: () => api.survey.questionAverages(pilotTag, versionB),
    enabled: canCompare,
  })

  const chartData = useMemo(() => {
    if (!aggregate) return []
    return Object.entries(aggregate).map(([version, stats]) => ({
      version,
      'Avg SUS': stats.avg_sus,
      'Avg Ethics': stats.avg_ethics,
      count: stats.count,
    }))
  }, [aggregate])

  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <Link
          to={`/config/${configId}/results`}
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2"
        >
          <ArrowLeft size={14} /> Back to results
        </Link>
        <h1 className="text-lg font-semibold text-gray-900">
          SUS & Ethics details {config?.application_name ? `— ${config.application_name}` : ''}
        </h1>
        {pilotTag && <p className="text-xs text-gray-400 mt-0.5">Pilot: {pilotTag}</p>}
      </div>

      {!pilotTag && config && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
          This configuration has no <code className="font-mono">pilot_tag</code> set, so per-version
          breakdown and comparison aren't available — only the single aggregated score shown on the
          results page.
        </div>
      )}

      {pilotTag && (
        <>
          {/* Per-version overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Average score by app version</h2>
            {aggregateLoading && (
              <div className="flex items-center justify-center h-40 gap-2 text-gray-400 text-sm">
                <Loader2 size={16} className="animate-spin" /> Loading…
              </div>
            )}
            {!aggregateLoading && chartData.length === 0 && (
              <p className="text-xs text-gray-400">No survey responses for this pilot yet.</p>
            )}
            {!aggregateLoading && chartData.length > 0 && (
              <ResponsiveContainer width="100%" height={Math.max(chartData.length * 50 + 40, 140)}>
                <BarChart data={chartData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                  <XAxis dataKey="version" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                  <Tooltip content={<VersionBarTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="Avg SUS" fill="#6366f1" radius={[3, 3, 0, 0]} maxBarSize={40} />
                  <Bar dataKey="Avg Ethics" fill="#14b8a6" radius={[3, 3, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Version comparison */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Compare two versions</h2>
            <div className="flex flex-wrap gap-3 mb-4">
              <select
                value={versionA}
                onChange={(e) => setVersionA(e.target.value)}
                className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-700"
              >
                <option value="">Version A…</option>
                {(versions ?? []).map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
              <select
                value={versionB}
                onChange={(e) => setVersionB(e.target.value)}
                className="rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-700"
              >
                <option value="">Version B…</option>
                {(versions ?? []).map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>

            {!canCompare && (
              <p className="text-xs text-gray-400">Pick two different versions to compare.</p>
            )}

            {canCompare && compareData && (
              <div className="space-y-5">
                <div className="flex flex-wrap gap-3">
                  <div className="rounded-md bg-indigo-50 px-3 py-2 text-xs text-indigo-700">
                    {versionA}: SUS {compareData.A.avg_sus.toFixed(1)} · Ethics {compareData.A.avg_ethics.toFixed(1)} · n={compareData.A.count}
                  </div>
                  <div className="rounded-md bg-teal-50 px-3 py-2 text-xs text-teal-700">
                    {versionB}: SUS {compareData.B.avg_sus.toFixed(1)} · Ethics {compareData.B.avg_ethics.toFixed(1)} · n={compareData.B.count}
                  </div>
                  <div className={clsx(
                    'rounded-md px-3 py-2 text-xs font-medium',
                    compareData.B.avg_sus >= compareData.A.avg_sus ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700',
                  )}>
                    Δ SUS {(compareData.B.avg_sus - compareData.A.avg_sus) >= 0 ? '+' : ''}
                    {(compareData.B.avg_sus - compareData.A.avg_sus).toFixed(1)}
                  </div>
                  <div className={clsx(
                    'rounded-md px-3 py-2 text-xs font-medium',
                    compareData.B.avg_ethics >= compareData.A.avg_ethics ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700',
                  )}>
                    Δ Ethics {(compareData.B.avg_ethics - compareData.A.avg_ethics) >= 0 ? '+' : ''}
                    {(compareData.B.avg_ethics - compareData.A.avg_ethics).toFixed(1)}
                  </div>
                </div>

                {qaA && qaB && (
                  <div className="space-y-4">
                    <p className="text-xs text-gray-400">
                      Per-question averages on a 1–5 scale (darker/greener = higher agreement).
                    </p>
                    <QuestionCompareTable
                      title="SUS questions"
                      questions={SUS_QUESTIONS}
                      avgA={qaA.sus}
                      avgB={qaB.sus}
                      versionA={versionA}
                      versionB={versionB}
                    />
                    <QuestionCompareTable
                      title="Ethics questions"
                      questions={ETHICS_QUESTIONS}
                      avgA={qaA.ethics}
                      avgB={qaB.ethics}
                      versionA={versionA}
                      versionB={versionB}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* Explanatory panels */}
      <div className="space-y-2">
        <QuestionExplainer title="What do the SUS questions ask?" questions={SUS_QUESTIONS} />
        <QuestionExplainer title="What do the Ethics questions ask?" questions={ETHICS_QUESTIONS} />
      </div>
    </div>
  )
}
