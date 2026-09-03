import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, AlertTriangle, Loader2, ChevronRight, Lock, Plus, X, Download } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../../services/api'

const INPUT = 'w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300'
const LABEL = 'mb-1 block text-xs font-medium text-gray-600'

function friendlyError(e) {
  return e?.message || 'Something went wrong'
}

// ── stepper shell (same pattern as FitAndSimulateFlow.jsx's wizard) ──────

function StepBreadcrumb({ stage }) {
  const steps = ['Setup', 'Predict (blind)', 'Reveal & compare']
  return (
    <div className="flex flex-wrap items-center gap-1.5 text-xs font-medium">
      {steps.map((label, i) => {
        const n = i + 1
        return (
          <span key={label} className="flex items-center gap-1.5">
            <span className={clsx(
              'rounded-full px-2 py-0.5',
              n < stage ? 'bg-indigo-100 text-indigo-700' : n === stage ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-400',
            )}>
              {n} {label}
            </span>
            {n < steps.length && <ChevronRight size={12} className="text-gray-300" />}
          </span>
        )
      })}
    </div>
  )
}

function StageCard({ index, stage, title, summary, children }) {
  const expanded = stage === index
  const done = stage > index
  return (
    <div className={clsx('rounded-lg border', expanded ? 'border-indigo-300 bg-white' : 'border-gray-200 bg-gray-50')}>
      <div className="flex items-center gap-2 px-4 py-2.5">
        {done ? (
          <CheckCircle2 size={16} className="flex-shrink-0 text-indigo-600" />
        ) : (
          <span className={clsx(
            'flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full text-[11px] font-semibold',
            expanded ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500',
          )}>
            {index}
          </span>
        )}
        <p className={clsx('text-sm font-semibold', expanded ? 'text-gray-800' : done ? 'text-gray-600' : 'text-gray-400')}>{title}</p>
        {!expanded && summary && <p className="ml-auto truncate text-xs text-gray-400">{summary}</p>}
      </div>
      {expanded && <div className="space-y-3 border-t border-gray-100 px-4 py-4">{children}</div>}
    </div>
  )
}

// ── Panel 1: Setup ────────────────────────────────────────────────────────

function SetupPanel({ ontology, onCreated }) {
  const [name, setName] = useState('')
  const [domain, setDomain] = useState('')
  const [sourceModelId, setSourceModelId] = useState('model_A')
  const [sourceFittedModelPath, setSourceFittedModelPath] = useState('')
  const [sourceLogFilePath, setSourceLogFilePath] = useState('')
  const [targets, setTargets] = useState([{ modelId: 'model_B', logFilePath: '' }])
  const [nSessions, setNSessions] = useState(20)
  const [nItems, setNItems] = useState(164)
  const [progressText, setProgressText] = useState('')

  // Fitted model path defaults from the domain's own ontology entry, same
  // placeholder-from-ontology convention ProbabilisticRunForm uses - set on
  // the domain select's own onChange (not via effect) and only if the user
  // hasn't already typed something themselves.
  function handleDomainChange(nextDomain) {
    setDomain(nextDomain)
    if (sourceFittedModelPath) return
    const d = (ontology?.domains ?? []).find((x) => x.id === nextDomain)
    if (d?.fitted_model) setSourceFittedModelPath(d.fitted_model)
  }

  function updateTarget(i, field, value) {
    setTargets((ts) => ts.map((t, idx) => (idx === i ? { ...t, [field]: value } : t)))
  }
  function addTarget() {
    setTargets((ts) => [...ts, { modelId: `model_${String.fromCharCode(66 + ts.length)}`, logFilePath: '' }])
  }
  function removeTarget(i) {
    setTargets((ts) => ts.filter((_, idx) => idx !== i))
  }

  const createMutation = useMutation({
    mutationFn: async () => {
      setProgressText('Creating experiment…')
      const exp = await api.experiments.create({
        name: name.trim(),
        domain,
        source_model_id: sourceModelId.trim(),
        n_sessions: Number(nSessions),
        n_items: Number(nItems),
      })

      setProgressText(`Registering ${sourceModelId}…`)
      await api.experiments.registerModel(exp.experiment_id, {
        model_id: sourceModelId.trim(),
        role: 'source',
        fitted_model_path: sourceFittedModelPath.trim() || null,
        log_file_path: sourceLogFilePath.trim() || null,
      })

      for (const t of targets) {
        setProgressText(`Registering ${t.modelId}…`)
        await api.experiments.registerModel(exp.experiment_id, {
          model_id: t.modelId.trim(),
          role: 'target',
          log_file_path: t.logFilePath.trim(),
        })
      }

      return exp
    },
    onSuccess: (exp) => onCreated(exp.experiment_id),
  })

  const canCreate = (
    name.trim() && domain && sourceModelId.trim() && sourceFittedModelPath.trim()
    && targets.length > 0 && targets.every((t) => t.modelId.trim() && t.logFilePath.trim())
    && !createMutation.isPending
  )

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className={LABEL}>Experiment name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. SC three-model study" className={INPUT} />
        </div>
        <div>
          <label className={LABEL}>Domain</label>
          <select value={domain} onChange={(e) => handleDomainChange(e.target.value)} className={INPUT}>
            <option value="">Choose a domain…</option>
            {(ontology?.domains ?? []).map((d) => <option key={d.id} value={d.id}>{d.label}</option>)}
          </select>
        </div>
      </div>

      <div className="rounded-md border border-gray-100 bg-gray-50 p-3">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Source model</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div>
            <label className={LABEL}>Model ID</label>
            <input type="text" value={sourceModelId} onChange={(e) => setSourceModelId(e.target.value)} className={INPUT} />
          </div>
          <div>
            <label className={LABEL}>Fitted model path</label>
            <input
              type="text" value={sourceFittedModelPath} onChange={(e) => setSourceFittedModelPath(e.target.value)}
              placeholder="data/sc_markov_model.json" className={INPUT}
            />
          </div>
          <div>
            <label className={LABEL}>Log file path (optional)</label>
            <input
              type="text" value={sourceLogFilePath} onChange={(e) => setSourceLogFilePath(e.target.value)}
              placeholder="only needed if re-fitting" className={INPUT}
            />
          </div>
        </div>
      </div>

      <div className="rounded-md border border-gray-100 bg-gray-50 p-3">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Target models</p>
        <div className="space-y-2">
          {targets.map((t, i) => (
            <div key={i} className="flex flex-col gap-2 sm:flex-row sm:items-end">
              <div className="flex-1">
                <label className={LABEL}>Model ID</label>
                <input type="text" value={t.modelId} onChange={(e) => updateTarget(i, 'modelId', e.target.value)} className={INPUT} />
              </div>
              <div className="flex-[2]">
                <label className={LABEL}>Log file path</label>
                <input
                  type="text" value={t.logFilePath} onChange={(e) => updateTarget(i, 'logFilePath', e.target.value)}
                  placeholder="path to this model's interaction logs" className={INPUT}
                />
              </div>
              <button
                type="button" onClick={() => removeTarget(i)} disabled={targets.length <= 1}
                className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-2.5 py-1.5 text-xs font-medium text-gray-500 transition-colors hover:bg-white disabled:opacity-40"
              >
                <X size={12} /> Remove
              </button>
            </div>
          ))}
        </div>
        <button
          type="button" onClick={addTarget}
          className="mt-2 inline-flex items-center gap-1 rounded-md border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-indigo-600 transition-colors hover:bg-indigo-50"
        >
          <Plus size={12} /> Add target model
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={LABEL}>Sessions per prediction</label>
          <input type="number" min={1} value={nSessions} onChange={(e) => setNSessions(e.target.value)} className={INPUT} />
        </div>
        <div>
          <label className={LABEL}>Items per session</label>
          <input type="number" min={1} value={nItems} onChange={(e) => setNItems(e.target.value)} className={INPUT} />
        </div>
      </div>

      <button
        type="button" disabled={!canCreate} onClick={() => createMutation.mutate()}
        className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {createMutation.isPending && <Loader2 size={14} className="animate-spin" />}
        {createMutation.isPending ? progressText : 'Create experiment'} <ChevronRight size={14} />
      </button>

      {createMutation.isError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {friendlyError(createMutation.error)}
        </div>
      )}
    </div>
  )
}

// ── Panel 2: Predict (blind) ─────────────────────────────────────────────

function PredictPanel({ experimentId, onContinue }) {
  const queryClient = useQueryClient()
  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', experimentId],
    queryFn: () => api.experiments.get(experimentId),
  })
  const [extractStatus, setExtractStatus] = useState({})

  const source = (experiment?.models ?? []).find((m) => m.role === 'source')
  const targetModels = (experiment?.models ?? []).filter((m) => m.role === 'target')

  const extractMutation = useMutation({
    mutationFn: async () => {
      for (const t of targetModels) {
        setExtractStatus((s) => ({ ...s, [t.model_id]: { status: 'extracting' } }))
        try {
          const res = await api.experiments.extract(experimentId, t.model_id)
          setExtractStatus((s) => ({ ...s, [t.model_id]: { status: 'done', freq: res.ai_action_frequency } }))
        } catch (e) {
          setExtractStatus((s) => ({ ...s, [t.model_id]: { status: 'error', error: friendlyError(e) } }))
        }
      }
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] }),
  })

  const predictMutation = useMutation({
    mutationFn: async () => {
      const results = {}
      for (const t of targetModels) {
        results[t.model_id] = await api.experiments.predict(experimentId, t.model_id)
      }
      return results
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] }),
  })

  const allExtracted = targetModels.length > 0 && targetModels.every((t) => extractStatus[t.model_id]?.status === 'done')
  const sealedAt = predictMutation.data
    ? Object.values(predictMutation.data)[0]?.predictions_sealed_at
    : null

  if (isLoading) {
    return <div className="flex items-center gap-2 text-sm text-gray-400"><Loader2 size={14} className="animate-spin" /> Loading experiment…</div>
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-600">
        <p><span className="font-medium text-gray-700">Source:</span> {source?.model_id} (fitted: {source?.fitted_model_path || 'none'})</p>
        <p><span className="font-medium text-gray-700">Targets:</span> {targetModels.map((t) => t.model_id).join(', ')}</p>
      </div>

      <div className="space-y-2 rounded-md border border-indigo-100 bg-indigo-50 p-3 text-xs text-indigo-800">
        <p><span className="font-semibold">Phase 1:</span> We extract only the AI decisions from your target model logs — not the operator responses. Operator data stays hidden until you choose to reveal it.</p>
        <p><span className="font-semibold">Phase 2:</span> We use the source model's surrogate to predict HAIC metrics for each target model.</p>
      </div>

      {!allExtracted && (
        <button
          type="button" disabled={extractMutation.isPending} onClick={() => extractMutation.mutate()}
          className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {extractMutation.isPending && <Loader2 size={14} className="animate-spin" />}
          Extract AI frequencies <ChevronRight size={14} />
        </button>
      )}

      {targetModels.length > 0 && Object.keys(extractStatus).length > 0 && (
        <div className="space-y-1.5">
          {targetModels.map((t) => {
            const st = extractStatus[t.model_id]
            return (
              <div key={t.model_id} className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-medium text-gray-700">{t.model_id}:</span>
                {!st && <span className="text-gray-400">not started</span>}
                {st?.status === 'extracting' && <span className="inline-flex items-center gap-1 text-gray-500"><Loader2 size={11} className="animate-spin" /> extracting…</span>}
                {st?.status === 'done' && (
                  <span className="inline-flex items-center gap-1 text-green-700">
                    <CheckCircle2 size={11} /> ai_reject: {(st.freq.ai_reject * 100).toFixed(1)}%, ai_flag: {(st.freq.ai_flag * 100).toFixed(1)}%
                  </span>
                )}
                {st?.status === 'error' && <span className="inline-flex items-center gap-1 text-red-600"><AlertTriangle size={11} /> {st.error}</span>}
              </div>
            )
          })}
        </div>
      )}

      {allExtracted && !predictMutation.data && (
        <button
          type="button" disabled={predictMutation.isPending} onClick={() => predictMutation.mutate()}
          className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {predictMutation.isPending && <Loader2 size={14} className="animate-spin" />}
          Generate blind predictions <ChevronRight size={14} />
        </button>
      )}

      {predictMutation.isError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {friendlyError(predictMutation.error)}
        </div>
      )}

      {predictMutation.data && (
        <div className="space-y-3">
          <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
            <p className="flex items-center gap-1.5 font-semibold"><Lock size={12} /> Predictions sealed at {sealedAt ? new Date(sealedAt).toLocaleString() : 'unknown'}</p>
            <p className="mt-0.5">Operator data for {targetModels.map((t) => t.model_id).join(' and ')} has not been used.</p>
          </div>

          {Object.entries(predictMutation.data).map(([modelId, res]) => (
            <div key={modelId} className="rounded-md border border-gray-200 p-3 text-xs">
              <p className="mb-1.5 font-medium text-gray-700">{modelId} predictions:</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-gray-600 sm:grid-cols-4">
                {['Tr', 'HCL', 'EL', 'F'].map((m) => (
                  <p key={m}>
                    {m}: {res.predictions[m].mean != null ? res.predictions[m].mean.toFixed(3) : 'N/A'}
                    {res.predictions[m].std != null && ` ± ${res.predictions[m].std.toFixed(3)}`}
                  </p>
                ))}
              </div>
            </div>
          ))}

          <button
            type="button" onClick={onContinue}
            className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
          >
            Continue to reveal <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  )
}

// ── Panel 3: Reveal & compare ─────────────────────────────────────────────

function ComparisonTable({ c }) {
  const rows = [
    ['Tr', c.predicted.Tr, c.real.Tr, c.errors.Tr_pct],
    ['HCL', c.predicted.HCL, c.real.HCL, c.errors.HCL_pct],
    ['EL', c.predicted.EL, c.real.EL, c.errors.EL_pct],
    ['F', c.predicted.F, c.real.F, c.errors.F_pct],
  ]
  const fmt = (v) => (v == null ? 'N/A' : v.toFixed(3))
  const fmtPct = (v) => (v == null ? 'N/A' : `${v.toFixed(1)}%`)

  return (
    <div className="space-y-2 rounded-md border border-gray-200 p-3 text-xs">
      <p className="font-medium text-gray-700">Comparison: {c.model_a} → {c.model_b}</p>
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th className="px-2 py-1.5 text-left font-medium">Metric</th>
              <th className="px-2 py-1.5 text-left font-medium">Predicted</th>
              <th className="px-2 py-1.5 text-left font-medium">Real</th>
              <th className="px-2 py-1.5 text-left font-medium">Error%</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([metric, pred, real, err]) => (
              <tr key={metric} className="border-t border-gray-100 text-gray-700">
                <td className="px-2 py-1.5 font-mono">{metric}</td>
                <td className="px-2 py-1.5">{fmt(pred?.mean)}</td>
                <td className="px-2 py-1.5">{fmt(real)}</td>
                <td className="px-2 py-1.5">{fmtPct(err)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="pt-1 text-gray-700">
        Cross-model S({c.model_a}→{c.model_b}): <span className="font-medium">{fmt(c.S_cross)}</span>
      </p>
      {c.S_cross_per_action && (
        <p className="text-gray-500">
          {Object.entries(c.S_cross_per_action).map(([ai, v]) => `${ai}: ${v.toFixed(3)}`).join('  ')}
        </p>
      )}

      <div className="space-y-1 pt-1">
        <p className="font-medium text-gray-700">Hypothesis verdicts:</p>
        <p className={c.hypotheses.H1 ? 'text-green-700' : 'text-red-600'}>
          {c.hypotheses.H1 ? '✓ SUPPORTED' : '✗ REJECTED'} — H1 (frequency transfer): error &lt; 15%
        </p>
        <p className={c.hypotheses.H2 ? 'text-green-700' : 'text-red-600'}>
          {c.hypotheses.H2 ? '✓ SUPPORTED' : '✗ REJECTED'} — H2 (matrix stability): S = {fmt(c.S_cross)} &gt; 0.80
        </p>
        <p className={c.hypotheses.H3 ? 'text-green-700' : 'text-red-600'}>
          {c.hypotheses.H3 ? '✓ SUPPORTED' : '✗ REJECTED'} — H3 (regime decomposition)
        </p>
      </div>
    </div>
  )
}

function RevealComparePanel({ experimentId }) {
  const queryClient = useQueryClient()
  const { data: experiment } = useQuery({
    queryKey: ['experiment', experimentId],
    queryFn: () => api.experiments.get(experimentId),
  })
  const targetModels = (experiment?.models ?? []).filter((m) => m.role === 'target')

  const revealMutation = useMutation({
    mutationFn: (modelId) => api.experiments.reveal(experimentId, modelId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] }),
  })
  const [revealingId, setRevealingId] = useState(null)

  // run/compare's own response is the engine's flat phase_3 output
  // (pred_Tr, err_Tr_pct, h1_supported, ...) - the nested {predicted,
  // real, errors, hypotheses} shape the table below is built for only
  // comes from GET /results, which is also what the task spec says this
  // table should match. So compare just triggers the analysis; results
  // are then fetched separately once it succeeds.
  const compareMutation = useMutation({
    mutationFn: () => api.experiments.compare(experimentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['experiment-results', experimentId] }),
  })

  const { data: resultsReport } = useQuery({
    queryKey: ['experiment-results', experimentId],
    queryFn: () => api.experiments.results(experimentId),
    enabled: compareMutation.isSuccess,
  })

  const allRevealed = targetModels.length > 0 && targetModels.every((t) => t.status === 'revealed')
  const comparisons = resultsReport?.comparisons ?? []

  async function handleReveal(modelId) {
    setRevealingId(modelId)
    try {
      await revealMutation.mutateAsync(modelId)
    } finally {
      setRevealingId(null)
    }
  }

  async function handleExport() {
    const report = await api.experiments.resultsExport(experimentId)
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `experiment_${experimentId}_results.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
        <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
        Once you reveal a model's real operator data, it cannot be un-revealed. The blind prediction is already
        sealed with a timestamp — revealing confirms the experiment.
      </div>

      <div className="space-y-2">
        {targetModels.map((t) => {
          const revealed = t.status === 'revealed'
          return (
            <div key={t.model_id} className="rounded-md border border-gray-200 p-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium text-gray-700">{t.model_id}</p>
                {revealed ? (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700"><CheckCircle2 size={12} /> revealed</span>
                ) : (
                  <span className="text-xs text-gray-400">sealed — not yet revealed</span>
                )}
              </div>
              {!revealed && (
                <button
                  type="button" disabled={revealingId === t.model_id}
                  onClick={() => handleReveal(t.model_id)}
                  className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
                >
                  {revealingId === t.model_id && <Loader2 size={12} className="animate-spin" />}
                  Reveal {t.model_id} real data <ChevronRight size={12} />
                </button>
              )}
              {revealed && (
                <p className="mt-1 text-xs text-gray-500">Real matrix fitted: {t.fitted_model_path}</p>
              )}
            </div>
          )
        })}
      </div>

      {revealMutation.isError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {friendlyError(revealMutation.error)}
        </div>
      )}

      {allRevealed && comparisons.length === 0 && (
        <button
          type="button" disabled={compareMutation.isPending} onClick={() => compareMutation.mutate()}
          className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {compareMutation.isPending && <Loader2 size={14} className="animate-spin" />}
          Run comparison analysis <ChevronRight size={14} />
        </button>
      )}

      {compareMutation.isError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {friendlyError(compareMutation.error)}
        </div>
      )}

      {comparisons.length > 0 && (
        <div className="space-y-3">
          {comparisons.map((c) => <ComparisonTable key={`${c.model_a}-${c.model_b}`} c={c} />)}
          <button
            type="button" onClick={handleExport}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <Download size={12} /> Export results JSON
          </button>
        </div>
      )}
    </div>
  )
}

// ── Main component ───────────────────────────────────────────────────────

export default function MultiModelExperiment() {
  const { data: ontology } = useQuery({ queryKey: ['ontology'], queryFn: () => api.ontology.get() })
  const [stage, setStage] = useState(1)
  const [experimentId, setExperimentId] = useState(null)

  return (
    <div className="space-y-3">
      <StepBreadcrumb stage={stage} />

      <StageCard index={1} stage={stage} title="Setup" summary={experimentId ? `Experiment ${experimentId.slice(0, 8)}…` : null}>
        <SetupPanel ontology={ontology} onCreated={(id) => { setExperimentId(id); setStage(2) }} />
      </StageCard>

      {experimentId && (
        <StageCard index={2} stage={stage} title="Predict (blind)">
          <PredictPanel experimentId={experimentId} onContinue={() => setStage(3)} />
        </StageCard>
      )}

      {experimentId && stage >= 3 && (
        <StageCard index={3} stage={stage} title="Reveal & compare">
          <RevealComparePanel experimentId={experimentId} />
        </StageCard>
      )}
    </div>
  )
}
