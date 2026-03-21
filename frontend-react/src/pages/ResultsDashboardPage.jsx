import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useQueries } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts'
import { ArrowLeft, Loader2, AlertCircle, Sparkles } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import QuadrantPlot, { PALETTE } from '../components/QuadrantPlot'
import MetricCard from '../components/MetricCard'
import OutcomeView from '../components/OutcomeView'

const CORE_METRICS = ['F', 'D', 'HCL', 'Tr', 'A', 'S', 'EL', 'EfficiencyScore']
const LOWER_BETTER = new Set(['EL', 'D'])

function deriveDomain(config) {
  const text = `${config?.application_name ?? ''} ${config?.description ?? ''}`.toLowerCase()
  if (/health|medical|clinic|hospital/.test(text)) return 'healthcare'
  if (/energy|power|grid|electric/.test(text)) return 'energy'
  return 'applications'
}

function InterpretationPanel({ interaction, warnings, pilotTag }) {
  const [narrative, setNarrative] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function generate() {
    setLoading(true)
    setError(null)
    try {
      const result = await api.interpret({
        pilot_tag: pilotTag,
        metrics: interaction,
        warnings: warnings,
      })
      setNarrative(result.narrative)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-700">AI Interpretation</h3>
        </div>
        {!narrative && (
          <button
            disabled={loading}
            onClick={generate}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium
                       bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading
              ? <><Loader2 size={11} className="animate-spin" /> Generating…</>
              : 'Generate interpretation'}
          </button>
        )}
        {narrative && (
          <button
            onClick={() => { setNarrative(null); setError(null) }}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            Reset
          </button>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-red-700 text-xs">
          <AlertCircle size={12} className="mt-0.5 flex-shrink-0" />
          {error}
        </div>
      )}

      {narrative && (
        <div className="text-sm text-gray-700 leading-relaxed space-y-3 whitespace-pre-line">
          {narrative}
        </div>
      )}

      {!narrative && !loading && !error && (
        <p className="text-xs text-gray-400">
          Click to generate a plain-language interpretation of the collaboration metrics for this pilot.
        </p>
      )}
    </div>
  )
}

function bestVersion(metric, data) {
  const valid = data.filter(d => d.value != null)
  if (!valid.length) return null
  return LOWER_BETTER.has(metric)
    ? valid.reduce((b, d) => d.value < b.value ? d : b).version
    : valid.reduce((b, d) => d.value > b.value ? d : b).version
}

function SegmentToggle({ options, value, onChange }) {
  return (
    <div className="flex items-center bg-gray-100 rounded-lg p-1 gap-0.5">
      {options.map(([v, label]) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={clsx(
            'px-4 py-1.5 text-sm rounded-md font-medium transition-colors',
            value === v
              ? 'bg-white shadow-sm text-gray-900'
              : 'text-gray-500 hover:text-gray-700',
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )
}

function SmallToggle({ options, value, onChange }) {
  return (
    <div className="flex items-center bg-gray-100 rounded-lg p-1 gap-0.5">
      {options.map(([v, label]) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={clsx(
            'px-3 py-1 text-xs rounded-md capitalize font-medium transition-colors',
            value === v
              ? 'bg-white shadow-sm text-gray-800'
              : 'text-gray-500 hover:text-gray-700',
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )
}

function VersionTabs({ versions, selectedIdx, onSelect }) {
  if (versions.length <= 1) return null
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-xs text-gray-400">Version:</span>
      {versions.map((v, i) => (
        <button
          key={v}
          onClick={() => onSelect(i)}
          className={clsx(
            'flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition-colors',
            selectedIdx === i
              ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
              : 'border-gray-200 text-gray-600 hover:border-gray-300 bg-white',
          )}
        >
          <span
            className="inline-block w-2 h-2 rounded-full"
            style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
          />
          {v}
        </button>
      ))}
    </div>
  )
}

function VersionBarChart({ results, compMetric, setCompMetric }) {
  const barData = results.map((r, i) => ({
    version: r.ai_model_version,
    value: r.aggregates?.interaction?.[compMetric] ?? null,
    color: PALETTE[i % PALETTE.length],
  }))
  const best = bestVersion(compMetric, barData)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">Version Comparison</h3>
        <select
          value={compMetric}
          onChange={e => setCompMetric(e.target.value)}
          className="text-sm border border-gray-200 rounded px-2 py-1 text-gray-700
                     focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          {CORE_METRICS.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={barData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
          <XAxis dataKey="version" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]
              return (
                <div className="bg-white border border-gray-200 rounded shadow-sm text-xs p-2 space-y-0.5">
                  <p className="font-semibold text-gray-800">{d.payload?.version}</p>
                  <p className="text-gray-500">
                    {compMetric}: <span className="font-mono">{d.value?.toFixed(3) ?? '—'}</span>
                  </p>
                  {d.payload?.version === best && (
                    <p className="text-green-600 font-medium">Best version</p>
                  )}
                </div>
              )
            }}
          />
          <Bar dataKey="value" maxBarSize={60} radius={[3, 3, 0, 0]}>
            {barData.map((d, i) => (
              <Cell
                key={i}
                fill={d.version === best ? '#10b981' : PALETTE[i % PALETTE.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {best && (
        <p className="text-xs text-gray-400 mt-2 text-right">
          Best: <span className="font-medium text-green-600">{best}</span>
          {LOWER_BETTER.has(compMetric) ? ' (lowest)' : ' (highest)'}
        </p>
      )}
    </div>
  )
}

export default function ResultsDashboardPage() {
  const { id } = useParams()
  const configId = Number(id)

  const [mode, setMode] = useState('core')
  const [audience, setAudience] = useState('researcher')
  const [selectedIdx, setSelectedIdx] = useState(0)
  const [compMetric, setCompMetric] = useState('Tr')

  // Config metadata
  const { data: config } = useQuery({
    queryKey: ['config', configId],
    queryFn: () => api.configs.get(configId),
  })

  // Result stubs list — treat 404 as empty
  const { data: stubs, isLoading: stubsLoading, error: stubsError } = useQuery({
    queryKey: ['result-stubs', configId],
    queryFn: async () => {
      try {
        return await api.results.list(configId)
      } catch (e) {
        if (e.message?.includes('No results found')) return []
        throw e
      }
    },
  })

  // Fetch full MinIO result data for each stub
  const resultQueries = useQueries({
    queries: (stubs ?? []).map(stub => ({
      queryKey: ['result-detail', configId, stub.id],
      queryFn: () => api.results.get(configId, stub.id),
      enabled: stubs != null && stubs.length > 0,
    })),
  })

  const results = resultQueries.map(q => q.data).filter(Boolean)
  const detailsLoading = (stubs?.length ?? 0) > 0 && !resultQueries.every(q => q.isFetched)

  const versions = results.map(r => r.ai_model_version)
  const safeIdx = results.length > 0 ? Math.min(selectedIdx, results.length - 1) : 0

  // Build quadrant data
  const quadrantPoints = results.map((r, i) => ({
    version: r.ai_model_version,
    color: PALETTE[i % PALETTE.length],
    ...(r.aggregates?.interaction ?? {}),
  }))

  const elTrPoints = quadrantPoints.map(p => ({
    version: p.version, color: p.color,
    x: p.EL ?? null, y: p.Tr ?? null,
  }))

  const fValues = quadrantPoints.map(p => p.F).filter(v => v != null)
  const fRef = fValues.length
    ? fValues.reduce((a, b) => a + b, 0) / fValues.length
    : 10

  const fHclPoints = quadrantPoints.map(p => ({
    version: p.version, color: p.color,
    x: p.F ?? null, y: p.HCL ?? null,
  }))

  // Selected result for cards
  const selResult = results[safeIdx]
  const interaction = selResult?.aggregates?.interaction ?? {}
  const warnings = selResult?.warnings ?? []
  const domain = deriveDomain(config)

  // ── Loading / error states ──────────────────────────────────

  if (stubsLoading || detailsLoading) {
    return (
      <div className="flex items-center justify-center h-64 gap-2 text-gray-400 text-sm">
        <Loader2 size={16} className="animate-spin" />
        Loading results…
      </div>
    )
  }

  if (stubsError) {
    return (
      <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
        <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
        {stubsError.message}
      </div>
    )
  }

  // ── Page render ─────────────────────────────────────────────

  return (
    <div className="space-y-5">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <Link to="/configs" className="flex items-center gap-1 text-gray-400 hover:text-gray-600 transition-colors">
          <ArrowLeft size={14} />
          Configurations
        </Link>
        <span className="text-gray-300">/</span>
        <span className="font-medium text-gray-700">
          {config?.application_name ?? `Config #${configId}`}
        </span>
        {config?.ai_model_name && (
          <>
            <span className="text-gray-300">·</span>
            <span className="text-gray-400 text-xs">{config.ai_model_name}</span>
          </>
        )}
      </div>

      {/* Controls row */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <SegmentToggle
          options={[['core', 'Core HAIC'], ['outcome', 'Outcome Metrics']]}
          value={mode}
          onChange={setMode}
        />
        {mode === 'core' && (
          <SmallToggle
            options={[['researcher', 'Researcher'], ['partner', 'Partner']]}
            value={audience}
            onChange={setAudience}
          />
        )}
      </div>

      {/* No results */}
      {results.length === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center text-sm text-amber-700">
          No evaluation results yet.
          <br />
          <span className="text-amber-500 text-xs mt-1 block">
            Upload logs and trigger an evaluation first.
          </span>
        </div>
      )}

      {/* ── Core HAIC mode ── */}
      {results.length > 0 && mode === 'core' && (
        <div className="space-y-6">

          {/* Hero: quadrant scatter plots */}
          <div className="grid grid-cols-2 gap-4">
            <QuadrantPlot
              title="Effort Loss × Trust"
              points={elTrPoints}
              xLabel="EL (Effort Loss)"
              yLabel="Tr (Trust)"
              xRef={0}
              yRef={0.5}
              quadrants={{
                topLeft: 'Trusted but slow',
                topRight: 'Ideal collaboration',
                bottomLeft: 'Redesign needed',
                bottomRight: 'Efficient but untrusted',
              }}
            />
            <QuadrantPlot
              title="Interaction Frequency × Cognitive Load"
              points={fHclPoints}
              xLabel="F (Frequency)"
              yLabel="HCL (Cognitive Load)"
              xRef={fRef}
              yRef={0.5}
              quadrants={{
                topLeft: 'Overloaded',
                topRight: 'Smooth & active',
                bottomLeft: 'Low engagement',
                bottomRight: 'Smooth but passive',
              }}
            />
          </div>

          {/* Metric cards */}
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">Metric Cards</h2>
            <VersionTabs versions={versions} selectedIdx={safeIdx} onSelect={setSelectedIdx} />
          </div>

          <div className="grid grid-cols-4 gap-3">
            {CORE_METRICS.map(key => (
              <MetricCard
                key={key}
                metricKey={key}
                value={interaction[key] ?? null}
                audience={audience}
                domain={domain}
                warnings={warnings}
              />
            ))}
          </div>

          {/* Version comparison (only if >1 version) */}
          {results.length > 1 && (
            <VersionBarChart
              results={results}
              compMetric={compMetric}
              setCompMetric={setCompMetric}
            />
          )}

          {/* AI Interpretation */}
          <InterpretationPanel
            interaction={interaction}
            warnings={warnings}
            pilotTag={config?.application_name ?? 'general'}
          />
        </div>
      )}

      {/* ── Outcome metrics mode ── */}
      {results.length > 0 && mode === 'outcome' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">Outcome Metrics by Pillar</h2>
            <VersionTabs versions={versions} selectedIdx={safeIdx} onSelect={setSelectedIdx} />
          </div>
          <OutcomeView results={results} selectedIdx={safeIdx} />
        </div>
      )}
    </div>
  )
}
