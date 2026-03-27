import { useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useQueries, useQueryClient } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts'
import { AlertCircle, ArrowLeft, Loader2, Sparkles, X, AlertTriangle } from 'lucide-react'
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

function _localNarrative(interaction, warnings) {
  const fmt = (v, digits = 3) => (v == null ? 'N/A' : Number(v).toFixed(digits))

  const F   = interaction.F   ?? null
  const Tr  = interaction.Tr  ?? null
  const HCL = interaction.HCL ?? null
  const EL  = interaction.EL  ?? null
  const A   = interaction.A   ?? null

  const trustDesc = Tr == null  ? 'Trust data is unavailable (no correctness labels in log).'
    : Tr >= 0.8  ? `Trust is high (${fmt(Tr)}) — operators accept most AI decisions.`
    : Tr >= 0.5  ? `Trust is moderate (${fmt(Tr)}) — operators override AI decisions roughly half the time.`
    : `Trust is low (${fmt(Tr)}) — operators frequently override AI decisions. Review model reliability.`

  const hclDesc = HCL == null ? 'Cognitive load data is unavailable (no timing fields in log).'
    : HCL >= 0.7 ? `Human cognitive load is low (${fmt(HCL)}) — operators are comfortable with the pace.`
    : HCL >= 0.4 ? `Human cognitive load is moderate (${fmt(HCL)}) — response times approach acceptable limits.`
    : `Human cognitive load is high (${fmt(HCL)}) — operators may be struggling to keep up. Consider reducing AI output rate.`

  const freqDesc = F == null ? ''
    : `Interaction frequency is ${fmt(F, 1)} events/min.`

  const elDesc = EL == null ? 'Effort loss cannot be computed without a baseline (add baseline_s to session).'
    : EL <= 0.2  ? `Effort loss is low (${fmt(EL)}) — the AI-assisted workflow is close to the baseline speed.`
    : EL <= 0.5  ? `Effort loss is moderate (${fmt(EL)}) — the workflow is somewhat slower than baseline.`
    : `Effort loss is high (${fmt(EL)}) — the workflow is significantly slower than baseline. Check for inefficiencies.`

  const adaptDesc = A == null ? ''
    : A > 0.1  ? `Adaptability is positive (${fmt(A)}) — collaboration improved over the session.`
    : A < -0.1 ? `Adaptability is negative (${fmt(A)}) — collaboration degraded during the session.`
    : `Adaptability is near-neutral (${fmt(A)}) — no clear trend in collaboration quality.`

  const warnCount = warnings?.length ?? 0
  const warnNote = warnCount > 0
    ? `Note: ${warnCount} metric warning(s) were detected — some values may be less accurate due to missing log fields.`
    : ''

  return [
    `Overall: ${freqDesc} ${trustDesc}`,
    `Efficiency: ${hclDesc} ${elDesc}`,
    [adaptDesc, warnNote].filter(Boolean).join(' '),
  ].filter(s => s.trim()).join('\n\n')
}

function InterpretationPanel({ interaction, warnings, pilotTag }) {
  const [narrative, setNarrative] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [source, setSource] = useState(null)  // 'ai' | 'local'

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
      setSource('ai')
    } catch (e) {
      // Backend unavailable or API key not configured — generate locally.
      setNarrative(_localNarrative(interaction, warnings))
      setSource('local')
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
          <div className="flex items-center gap-2">
            {source === 'local' && (
              <span className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5">
                local summary
              </span>
            )}
            <button
              onClick={() => { setNarrative(null); setError(null); setSource(null) }}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              Reset
            </button>
          </div>
        )}
      </div>

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
          key={`${i}-${v}`}
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

function FairnessModal({ onClose, onSuccess }) {
  const fileRef = useRef(null)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleFile(f) {
    setRunning(true); setError(null); setResult(null)
    try {
      const text = await f.text()
      const payload = JSON.parse(text)
      const res = await api.fairness.evaluateFromLog(payload)
      setResult(res)
      onSuccess()
    } catch (e) {
      setError(e instanceof SyntaxError ? `Invalid JSON: ${e.message}` : e.message)
    } finally {
      setRunning(false)
    }
  }

  const overallAcc = result?.overall?.accuracy
  const hasDisparity = Math.abs(result?.demographic_parity_difference ?? 0) > 0.1

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-800">Fairness Evaluation</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={16} /></button>
        </div>

        <p className="text-xs text-gray-500 leading-relaxed">
          Upload a log file (JSON) containing AI decisions with{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">prediction</code>/{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">ai_decision</code>,{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">ground_truth</code>/{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">op_decision</code>, and a sensitive
          feature field (<code className="font-mono bg-gray-100 px-1 rounded">cohort</code>,{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">role</code>,{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">op_id</code>, or{' '}
          <code className="font-mono bg-gray-100 px-1 rounded">user_group</code>).
        </p>

        <input
          ref={fileRef}
          type="file"
          accept=".json,application/json"
          className="hidden"
          onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
        />

        {!result && (
          <button
            onClick={() => fileRef.current?.click()}
            disabled={running}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
                       text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700
                       transition-colors disabled:opacity-40"
          >
            {running ? <><Loader2 size={14} className="animate-spin" /> Analyzing…</> : 'Upload fairness data'}
          </button>
        )}

        {error && (
          <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-xs text-red-700">
            <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-gray-700">Results</p>
              {hasDisparity && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">
                  Disparity detected
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500">
              Demographic Parity Difference:{' '}
              <span className="font-mono font-semibold text-gray-700">
                {Number(result.demographic_parity_difference).toFixed(3)}
              </span>
            </p>
            <div className="space-y-1.5">
              {(result.groups ?? []).map(g => {
                const acc = result.by_group?.accuracy?.[g]
                const pct = acc != null ? Math.round(acc * 100) : null
                const isLow = overallAcc != null && acc != null && acc < overallAcc - 0.1
                return (
                  <div key={g} className="flex items-center gap-3">
                    <span className="text-xs text-gray-600 w-24 truncate">{g}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div
                        className={clsx('h-2 rounded-full', isLow ? 'bg-red-400' : 'bg-indigo-500')}
                        style={{ width: `${pct ?? 0}%` }}
                      />
                    </div>
                    <span className={clsx('text-xs font-mono w-10 text-right', isLow ? 'text-red-600' : 'text-gray-600')}>
                      {pct != null ? `${pct}%` : '—'}
                    </span>
                  </div>
                )
              })}
            </div>
            <p className="text-xs text-gray-400">{result.n_samples} samples across {result.groups?.length} groups</p>
            <button
              onClick={onClose}
              className="w-full px-4 py-2 rounded-lg text-xs font-medium border border-gray-200
                         text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
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
  const [fairnessModalOpen, setFairnessModalOpen] = useState(false)
  const queryClient = useQueryClient()

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

  // Holistic summary (lazy — only fetched when tab is active)
  const { data: holistic, isLoading: holisticLoading } = useQuery({
    queryKey: ['holistic', configId],
    queryFn: () => api.results.holistic(configId),
    enabled: mode === 'holistic',
    retry: false,
  })

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
          options={[['core', 'Core HAIC'], ['outcome', 'Outcome Metrics'], ['holistic', 'Holistic']]}
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

      {/* ── Holistic mode ── */}
      {mode === 'holistic' && (
        <div className="space-y-5">
          {holisticLoading && (
            <div className="flex items-center justify-center h-40 gap-2 text-gray-400 text-sm">
              <Loader2 size={16} className="animate-spin" /> Loading holistic summary…
            </div>
          )}

          {!holisticLoading && !holistic && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center text-sm text-amber-700">
              No evaluation results yet.
              <br />
              <span className="text-amber-500 text-xs mt-1 block">
                Upload logs and trigger an evaluation first.
              </span>
            </div>
          )}

          {holistic && (
            <>
              {/* HAIC compact summary */}
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">HAIC Metrics</h3>
                <div className="grid grid-cols-4 gap-3">
                  {['F', 'D', 'HCL', 'Tr', 'A', 'EL', 'S', 'EfficiencyScore'].map(k => {
                    const v = holistic.haic?.[k]
                    return (
                      <div key={k} className="bg-gray-50 rounded-md px-3 py-2 text-center">
                        <p className="text-xs font-semibold text-gray-500">{k}</p>
                        <p className="text-lg font-mono font-semibold text-gray-800 mt-0.5">
                          {v == null ? '—' : Number(v).toFixed(3)}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Fairness section */}
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Fairness</h3>
                {holistic.fairness ? (
                  <div className="space-y-3">
                    <p className="text-xs text-gray-500">
                      Demographic Parity Difference:{' '}
                      <span className="font-mono font-semibold text-gray-700">
                        {Number(holistic.fairness.demographic_parity_difference).toFixed(3)}
                      </span>
                      <span className="ml-2 text-gray-400">(0 = perfect parity)</span>
                    </p>
                    <div className="space-y-1.5">
                      {holistic.fairness.groups?.map(g => {
                        const acc = holistic.fairness.by_group?.accuracy?.[g]
                        const pct = acc != null ? Math.round(acc * 100) : null
                        return (
                          <div key={g} className="flex items-center gap-3">
                            <span className="text-xs text-gray-600 w-28 truncate">{g}</span>
                            <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                              <div
                                className="h-2 rounded-full bg-indigo-500"
                                style={{ width: `${pct ?? 0}%` }}
                              />
                            </div>
                            <span className="text-xs font-mono text-gray-600 w-10 text-right">
                              {pct != null ? `${pct}%` : '—'}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                    <p className="text-xs text-gray-400">
                      {holistic.fairness.n_samples} samples across {holistic.fairness.groups?.length} groups
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-xs text-gray-400 leading-relaxed">
                      Fairness evaluation requires <code className="font-mono bg-gray-100 px-1 rounded">prediction</code> or{' '}
                      <code className="font-mono bg-gray-100 px-1 rounded">ai_decision</code> +{' '}
                      <code className="font-mono bg-gray-100 px-1 rounded">ground_truth</code> or{' '}
                      <code className="font-mono bg-gray-100 px-1 rounded">op_decision</code> + a sensitive feature field
                      (cohort, role, op_id, or user_group) in your log events.
                    </p>
                    <button
                      onClick={() => setFairnessModalOpen(true)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium
                                 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
                    >
                      Upload fairness data →
                    </button>
                  </div>
                )}
              </div>

              {/* SUS section */}
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">User Experience (SUS)</h3>
                {holistic.sus ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-indigo-600">
                          {Number(holistic.sus.mean_sus).toFixed(1)}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">SUS score /100</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-teal-600">
                          {Number(holistic.sus.mean_ethics).toFixed(1)}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">Ethics score /100</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-semibold text-gray-600">{holistic.sus.count}</p>
                        <p className="text-xs text-gray-400 mt-0.5">responses</p>
                      </div>
                    </div>
                    <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                      <div
                        className={clsx(
                          'h-3 rounded-full transition-all',
                          holistic.sus.mean_sus >= 70 ? 'bg-green-500'
                            : holistic.sus.mean_sus >= 50 ? 'bg-amber-400'
                            : 'bg-red-400',
                        )}
                        style={{ width: `${Math.min(holistic.sus.mean_sus, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400">
                      {holistic.sus.mean_sus >= 70 ? 'Good usability (SUS ≥ 70)'
                        : holistic.sus.mean_sus >= 50 ? 'Marginal usability (SUS 50–70)'
                        : 'Poor usability (SUS < 50) — consider UX improvements'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-xs text-gray-400">
                      No surveys collected for this configuration. Share the survey link with your users
                      and include{' '}
                      <code className="font-mono bg-gray-100 px-1 rounded">
                        "configuration_id": {configId}
                      </code>{' '}
                      in the submission to link responses here.
                    </p>
                    <Link
                      to={`/survey?config_id=${configId}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium
                                 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
                    >
                      Submit a survey response →
                    </Link>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {fairnessModalOpen && (
        <FairnessModal
          onClose={() => setFairnessModalOpen(false)}
          onSuccess={() => queryClient.invalidateQueries({ queryKey: ['holistic', configId] })}
        />
      )}
    </div>
  )
}
