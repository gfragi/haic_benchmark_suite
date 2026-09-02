import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Loader2, CheckCircle2, AlertTriangle, Upload, Download, ChevronRight } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../../services/api'
import InfoTooltip from './InfoTooltip'
import FitAndSimulateFlow from './FitAndSimulateFlow'

const TIER_BADGE = {
  0: 'bg-gray-100 text-gray-600',
  1: 'bg-green-100 text-green-700',
  2: 'bg-amber-100 text-amber-700',
  3: 'bg-amber-100 text-amber-700',
}

function formatRange(range, higherIs) {
  let r
  if (Array.isArray(range)) {
    r = `${range[0]} to ${range[1] ?? '∞'}`
  } else {
    r = String(range)
  }
  return higherIs ? `${r} (higher = ${higherIs})` : r
}

const INPUT = 'w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300'
const LABEL = 'mb-1 block text-xs font-medium text-gray-600'

export default function ProbabilisticRunForm({ configurationId, onSuccess }) {
  const { data: ontology, isLoading, error: ontologyError } = useQuery({
    queryKey: ['ontology'],
    queryFn: () => api.ontology.get(),
  })

  const [entryMode, setEntryMode] = useState('template') // 'template' | 'byod'

  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [uploadError, setUploadError] = useState(null)

  const [name, setName] = useState('')
  const [domain, setDomain] = useState('')
  const [surrogateTier, setSurrogateTier] = useState(1)
  const [persona, setPersona] = useState('aggregate')
  const [fittedModel, setFittedModel] = useState('')
  const [nItems, setNItems] = useState(164)
  const [nSessions, setNSessions] = useState(10)
  const [rtMaxS, setRtMaxS] = useState(300)
  const [baselineS, setBaselineS] = useState('')
  const [metrics, setMetrics] = useState(['Tr', 'HCL', 'EL', 'F', 'S'])
  const [pilotTag, setPilotTag] = useState('surrogate_probabilistic')
  const [appVersion, setAppVersion] = useState('sim_v2.0.0')
  const [aiModelVersion, setAiModelVersion] = useState('markov-1.0')
  const [seed, setSeed] = useState(42)

  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [result, setResult] = useState(null)

  if (isLoading) {
    return (
      <div className="space-y-3 animate-pulse">
        <div className="h-24 rounded-md bg-gray-100" />
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="h-64 rounded-md bg-gray-100" />
          <div className="h-64 rounded-md bg-gray-100" />
          <div className="h-64 rounded-md bg-gray-100" />
        </div>
      </div>
    )
  }

  if (ontologyError) {
    return (
      <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> Failed to load ontology: {ontologyError.message}
      </div>
    )
  }

  const domainsById = Object.fromEntries((ontology.domains ?? []).map((d) => [d.id, d]))
  const tiersById = Object.fromEntries((ontology.surrogate_tiers ?? []).map((t) => [t.id, t]))
  const personasById = Object.fromEntries((ontology.persona_archetypes ?? []).map((p) => [p.id, p]))

  function applyTemplate(t) {
    setSelectedTemplateId(t.id)
    setName(t.label)
    setDomain(t.domain)
    setSurrogateTier(t.surrogate_tier)
    setPersona(t.default_persona)
    setFittedModel(t.fitted_model || '')
    setNItems(t.n_items)
    setNSessions(t.n_sessions)
    setRtMaxS(t.rt_max_s)
    setBaselineS(t.baseline_s ?? '')
    setMetrics(t.metrics)
    setUploadError(null)
  }

  function handleUpload(event) {
    const file = event.target.files?.[0]
    event.target.value = '' // allow re-uploading the same file later
    if (!file) return

    const reader = new FileReader()
    reader.onload = () => {
      try {
        const json = JSON.parse(reader.result)
        if (json.schema !== 'haic.scenario.v1') {
          setUploadError('Not a valid scenario file - expected "schema": "haic.scenario.v1".')
          return
        }
        setSelectedTemplateId('')
        setUploadError(null)
        setName(json.name || '')
        setDomain(json.domain || '')
        setSurrogateTier(json.surrogate_tier ?? 0)
        setNItems(json.n_items ?? 164)
        setNSessions(json.n_sessions ?? 10)
        setRtMaxS(json.rt_max_s ?? 300)
        setBaselineS(json.baseline_s ?? '')
        setMetrics(json.metrics ?? [])
        const surrogateAgent = (json.agents || []).find((a) => a.role === 'surrogate' || a.persona)
        setPersona(surrogateAgent?.persona || 'aggregate')
        setFittedModel(surrogateAgent?.fitted_model || '')
      } catch {
        setUploadError('Could not parse that file as JSON.')
      }
    }
    reader.readAsText(file)
  }

  function toggleMetric(id) {
    setMetrics((m) => (m.includes(id) ? m.filter((x) => x !== id) : [...m, id]))
  }

  function handleExport() {
    const scenario = {
      schema: 'haic.scenario.v1',
      name,
      domain,
      surrogate_tier: surrogateTier,
      rt_max_s: Number(rtMaxS),
      baseline_s: baselineS === '' ? null : Number(baselineS),
      n_items: Number(nItems),
      n_sessions: Number(nSessions),
      metrics,
      agents: [
        { id: 'ai1', role: 'ai_system' },
        surrogateTier >= 1
          ? { id: 'operator', role: 'surrogate', persona, fitted_model: fittedModel || undefined }
          : { id: 'operator', role: 'human_operator', persona },
      ],
    }
    const blob = new Blob([JSON.stringify(scenario, null, 2)], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${(name || 'scenario').toLowerCase().replace(/[^a-z0-9]+/g, '_')}.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  const canSubmit = name.trim() && domain && metrics.length > 0 && configurationId && !submitting

  async function handleSubmit() {
    if (!canSubmit) return
    setSubmitting(true)
    setSubmitError(null)
    setResult(null)
    try {
      const out = await api.simulate.runProbabilistic({
        name: name.trim(),
        configuration_id: Number(configurationId),
        domain,
        surrogate_tier: surrogateTier,
        rt_max_s: Number(rtMaxS),
        baseline_s: baselineS === '' ? null : Number(baselineS),
        n_items: Number(nItems),
        n_sessions: Number(nSessions),
        persona,
        fitted_model: fittedModel || null,
        metrics,
        pilot_tag: pilotTag.trim(),
        app_version: appVersion.trim(),
        ai_model_version: aiModelVersion.trim(),
        seed: Number(seed),
      })
      setResult(out)
      onSuccess?.(out)
    } catch (e) {
      setSubmitError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  const nDecisionsPreview = Number(nItems || 0) * Number(nSessions || 0) * 2
  const runtimeEstimateS = (Number(nSessions || 0) * 0.1).toFixed(1)

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-md border border-gray-200 bg-gray-50 p-0.5 text-xs font-medium">
        {[
          { id: 'template', label: 'Use a template' },
          { id: 'byod', label: 'Bring your own data' },
        ].map((m) => (
          <button
            key={m.id} type="button" onClick={() => setEntryMode(m.id)}
            className={clsx(
              'rounded px-3 py-1.5 transition-colors',
              entryMode === m.id ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-700',
            )}
          >
            {m.label}
          </button>
        ))}
      </div>

      {entryMode === 'byod' && (
        <FitAndSimulateFlow configurationId={configurationId} ontology={ontology} onSuccess={onSuccess} />
      )}

      {entryMode === 'template' && (
      <>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* LEFT: templates */}
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Templates</p>
          <div className="space-y-2">
            {(ontology.templates ?? []).map((t) => {
              const tier = tiersById[t.surrogate_tier]
              const planned = tier?.status !== 'available'
              return (
                <button
                  key={t.id}
                  type="button"
                  disabled={planned}
                  onClick={() => applyTemplate(t)}
                  className={clsx(
                    'w-full rounded-md border p-3 text-left transition-colors',
                    selectedTemplateId === t.id ? 'border-indigo-500 ring-1 ring-indigo-300 bg-indigo-50' : 'border-gray-200 hover:border-gray-300',
                    planned && 'opacity-50 cursor-not-allowed',
                  )}
                >
                  <div className="mb-1 flex items-center gap-1.5">
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500">
                      {domainsById[t.domain]?.label || t.domain}
                    </span>
                    <span className={clsx('rounded px-1.5 py-0.5 text-[10px] font-medium', TIER_BADGE[t.surrogate_tier])}>
                      {tier?.label || `Tier ${t.surrogate_tier}`}{planned && ' · planned'}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800">{t.label}</p>
                  <p className="mt-0.5 text-xs text-gray-500">{t.description}</p>
                </button>
              )
            })}
          </div>

          <div>
            <input id="scenario-upload" type="file" accept="application/json" className="hidden" onChange={handleUpload} />
            <label htmlFor="scenario-upload" className="inline-flex cursor-pointer items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800">
              <Upload size={12} /> Or upload a scenario JSON <ChevronRight size={12} />
            </label>
            {uploadError && <p className="mt-1 text-xs text-red-600">{uploadError}</p>}
          </div>
        </div>

        {/* MIDDLE: form */}
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Configuration</p>

          <div>
            <label className={LABEL}>Scenario name</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
          </div>

          <div>
            <label className={LABEL}>Domain</label>
            <select value={domain} onChange={(e) => setDomain(e.target.value)} className={INPUT}>
              <option value="">Choose a domain…</option>
              {(ontology.domains ?? []).map((d) => <option key={d.id} value={d.id}>{d.label}</option>)}
            </select>
          </div>

          <div>
            <label className={LABEL}>Surrogate tier</label>
            <div className="flex flex-wrap gap-1.5">
              {(ontology.surrogate_tiers ?? []).map((t) => {
                const disabled = t.status !== 'available'
                return (
                  <button
                    key={t.id}
                    type="button"
                    disabled={disabled}
                    onClick={() => setSurrogateTier(t.id)}
                    title={disabled ? `${t.label} - planned, not yet available` : t.description}
                    className={clsx(
                      'rounded-md border px-2.5 py-1.5 text-xs font-medium transition-colors',
                      surrogateTier === t.id ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300',
                      disabled && 'opacity-40 cursor-not-allowed',
                    )}
                  >
                    {t.label}
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <label className={LABEL}>Persona</label>
            <select value={persona} onChange={(e) => setPersona(e.target.value)} className={INPUT}>
              {(ontology.persona_archetypes ?? []).map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
            {personasById[persona]?.description && (
              <p className="mt-1 text-xs text-gray-400">{personasById[persona].description}</p>
            )}
          </div>

          {surrogateTier >= 1 && (
            <div>
              <label className={LABEL}>Fitted model path</label>
              <input
                type="text" value={fittedModel} onChange={(e) => setFittedModel(e.target.value)}
                placeholder={domainsById[domain]?.fitted_model || 'none for this domain yet'}
                className={INPUT}
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={LABEL}>Number of items</label>
              <input type="number" min={1} value={nItems} onChange={(e) => setNItems(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>Number of sessions</label>
              <input type="number" min={1} value={nSessions} onChange={(e) => setNSessions(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>RT max (seconds)</label>
              <input type="number" min={0} value={rtMaxS} onChange={(e) => setRtMaxS(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>Baseline time (s)</label>
              <input
                type="number" min={0} value={baselineS} onChange={(e) => setBaselineS(e.target.value)}
                placeholder="auto" className={INPUT}
              />
            </div>
          </div>

          <div>
            <label className={LABEL}>Metrics</label>
            <div className="space-y-1.5">
              {(ontology.metric_families ?? []).map((m) => (
                <label key={m.id} className="flex items-center gap-2 text-sm text-gray-700">
                  <input type="checkbox" checked={metrics.includes(m.id)} onChange={() => toggleMetric(m.id)} className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-300" />
                  {m.id} - {m.label}
                  <InfoTooltip label={`${m.id} - ${m.label}`} description={m.description} range={formatRange(m.range, m.higher_is)} requires={(m.requires || []).join(', ')} />
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className={LABEL}>Pilot tag</label>
            <input type="text" value={pilotTag} onChange={(e) => setPilotTag(e.target.value)} className={INPUT} />
          </div>

          <details className="rounded-md border border-gray-100 bg-gray-50 px-3 py-2">
            <summary className="cursor-pointer text-xs font-medium text-gray-500">Advanced</summary>
            <div className="mt-2 space-y-2">
              <div>
                <label className={LABEL}>App version</label>
                <input type="text" value={appVersion} onChange={(e) => setAppVersion(e.target.value)} className={INPUT} />
              </div>
              <div>
                <label className={LABEL}>AI model version</label>
                <input type="text" value={aiModelVersion} onChange={(e) => setAiModelVersion(e.target.value)} className={INPUT} />
              </div>
              <div>
                <label className={LABEL}>Seed</label>
                <input type="number" value={seed} onChange={(e) => setSeed(e.target.value)} className={INPUT} />
              </div>
            </div>
          </details>
        </div>

        {/* RIGHT: preview */}
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Preview</p>
          <div className="rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-600 space-y-1.5">
            <p className="font-medium text-gray-700">This run will generate:</p>
            <p>&bull; {nSessions || 0} sessions &times; {nItems || 0} items = {nDecisionsPreview} decisions</p>
            <p>&bull; Surrogate: {tiersById[surrogateTier]?.label || `Tier ${surrogateTier}`}</p>
            <p>&bull; Persona: {personasById[persona]?.label || persona}</p>
            <p>&bull; Metrics: {metrics.join(', ') || 'none selected'}</p>
            <p>&bull; Estimated runtime: ~{runtimeEstimateS}s</p>
          </div>
          <button
            onClick={handleExport}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <Download size={12} /> Export scenario JSON
          </button>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {submitting && <Loader2 size={14} className="animate-spin" />}
        {submitting ? `Generating ${nSessions} sessions…` : 'Generate & Ingest (Probabilistic)'}
      </button>
      {!configurationId && (
        <p className="text-xs text-gray-400">Pick a target configuration above first.</p>
      )}

      {submitError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {submitError}
        </div>
      )}

      {result && (
        <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700 space-y-1.5">
          <p className="flex items-center gap-1.5 font-medium">
            <CheckCircle2 size={14} /> Generated {result.n_sessions_generated} session(s), {result.n_decisions_total} decisions.
          </p>
          <p className="text-xs text-green-800">run_ids: {result.run_ids.join(', ')}</p>
          <Link to="/compare" className="inline-flex items-center gap-0.5 text-xs font-medium text-green-800 underline hover:text-green-900">
            Compare Versions <ChevronRight size={12} />
          </Link>
        </div>
      )}
      </>
      )}
    </div>
  )
}
