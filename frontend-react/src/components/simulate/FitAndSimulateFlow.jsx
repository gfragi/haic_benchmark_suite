import { useState, useRef, useCallback, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Upload, CheckCircle2, AlertTriangle, Loader2, ChevronRight, ChevronLeft } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../../services/api'

// Fixed structural convention this wizard assumes for uploaded logs -
// matches what backend/app/routers/ontology.py's POST /fit-model hardcodes
// server-side (_AI_ACTION_FIELD/_HUMAN_ACTION_FIELD) and what
// MarkovSurrogate.generate_session() itself writes, so a model fit from
// real data and one fit from that class's own output use the same paths.
// There's no UI control for these - only the *values* found there are
// domain-specific, and those are discovered from the upload.
const AI_ACTION_FIELD = 'payload.ai_decision'
const HUMAN_ACTION_FIELD = 'payload.op_decision'
const FIT_MODEL_MIN_VALID = 10

const INPUT = 'w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300'
const LABEL = 'mb-1 block text-xs font-medium text-gray-600'
const DOMAIN_RE = /^[a-z][a-z0-9_]*$/

// ── helpers ──────────────────────────────────────────────────────────────

function getPath(obj, path) {
  return path.split('.').reduce((cur, key) => (cur && typeof cur === 'object' ? cur[key] : undefined), obj)
}

// Accepts {"logs": [...]} (each session has a "decisions" list - the real
// HAIC log shape, e.g. haic_sim_mvp/examples/events_all_v0_patched.json)
// or a flat array of decision-event dicts. "sessions" is also accepted as
// an alias for extra leniency.
function flattenEvents(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.logs)) return data.logs.flatMap((s) => s.decisions || [])
  if (data && Array.isArray(data.sessions)) return data.sessions.flatMap((s) => s.decisions || [])
  return null
}

function collectFieldNames(events, sampleSize = 10) {
  const names = new Set()
  function walk(obj, prefix) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
      if (prefix) names.add(prefix)
      return
    }
    for (const [k, v] of Object.entries(obj)) {
      const path = prefix ? `${prefix}.${k}` : k
      if (v && typeof v === 'object' && !Array.isArray(v)) walk(v, path)
      else names.add(path)
    }
  }
  events.slice(0, sampleSize).forEach((e) => walk(e, ''))
  return [...names].sort()
}

function uniqueValuesAtField(events, field) {
  const values = new Set()
  events.forEach((e) => {
    const v = getPath(e, field)
    if (v !== undefined && v !== null) values.add(v)
  })
  return [...values]
}

function isNumericField(events, field, sampleSize = 20) {
  const sample = events.slice(0, sampleSize).map((e) => getPath(e, field)).filter((v) => v !== undefined && v !== null)
  if (!sample.length) return false
  return sample.every((v) => typeof v === 'number')
}

// Pairs events by interaction_id using the fixed AI/human action field
// paths - mirrors backend/app/routers/ontology.py's fit-model matching
// rule client-side, so the Stage 2 preview reflects what the server will
// actually do.
function pairInteractions(events, aiActorValue, humanActorValue) {
  if (!events || !aiActorValue || !humanActorValue) return []
  const byInteraction = new Map()
  for (const e of events) {
    const iid = e.interaction_id
    if (iid == null) continue
    if (!byInteraction.has(iid)) byInteraction.set(iid, [])
    byInteraction.get(iid).push(e)
  }
  const pairs = []
  for (const evs of byInteraction.values()) {
    const aiEvent = evs.find((e) => e.actor_type === aiActorValue && getPath(e, AI_ACTION_FIELD) != null)
    const humanEvent = evs.find((e) => e.actor_type === humanActorValue && getPath(e, HUMAN_ACTION_FIELD) != null)
    if (aiEvent && humanEvent) pairs.push({ aiEvent, humanEvent })
  }
  return pairs
}

function friendlyError(error) {
  if (!error) return null
  if (error.code === 'NO_VALID_PAIRS' || error.code === 'INSUFFICIENT_DATA') {
    return (
      `We found fewer than ${FIT_MODEL_MIN_VALID} usable interaction pairs in your file. The model needs at ` +
      `least ${FIT_MODEL_MIN_VALID} to be reliable. Check that your file contains both AI and human events for the same interactions.`
    )
  }
  return error.message
}

// ── Stage 1: Upload ─────────────────────────────────────────────────────

function UploadStage({ onContinue }) {
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState(null)
  const [preview, setPreview] = useState(null)
  const inputRef = useRef(null)

  function processFile(file) {
    setError(null)
    const reader = new FileReader()
    reader.onload = () => {
      let data
      try {
        data = JSON.parse(reader.result)
      } catch {
        setError('Could not parse this file as JSON')
        setPreview(null)
        return
      }
      const events = flattenEvents(data)
      if (!events || events.length === 0) {
        setError('No interaction records detected')
        setPreview(null)
        return
      }
      const fields = collectFieldNames(events)
      setPreview({ file, fileName: file.name, recordCount: events.length, fields, events })
    }
    reader.onerror = () => setError('Could not read this file')
    reader.readAsText(file)
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) processFile(file)
  }, [])

  return (
    <div className="space-y-3">
      <div
        onDragEnter={(e) => { e.preventDefault(); setDragging(true) }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={clsx(
          'flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-8 transition-colors',
          dragging ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50',
        )}
      >
        <Upload size={28} className="text-gray-300" />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-600">Drop your interaction log file here</p>
          <p className="mt-0.5 text-xs text-gray-400">JSON format · Any HAIC-compatible log</p>
        </div>
        <span className="text-xs font-medium text-indigo-600 hover:text-indigo-800">Or browse</span>
        <input
          ref={inputRef} type="file" accept="application/json,.json" className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; e.target.value = ''; if (f) processFile(f) }}
        />
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      {preview && (
        <div className="space-y-1 rounded-md border border-green-200 bg-green-50 p-3 text-xs text-green-800">
          <p className="flex items-center gap-1.5"><CheckCircle2 size={12} className="flex-shrink-0" /> File: {preview.fileName}</p>
          <p className="flex items-center gap-1.5"><CheckCircle2 size={12} className="flex-shrink-0" /> Records found: {preview.recordCount}</p>
          <p className="flex items-start gap-1.5"><CheckCircle2 size={12} className="mt-0.5 flex-shrink-0" /> Fields detected: {preview.fields.join(', ')}</p>
        </div>
      )}

      <div className="pt-1">
        <button
          type="button" disabled={!preview}
          onClick={() => onContinue(preview)}
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          Continue <ChevronRight size={12} />
        </button>
      </div>
    </div>
  )
}

// ── Stage 2: Map fields ──────────────────────────────────────────────────

function MapFieldsStage({ fileInfo, mapping, setMapping, onBack, onContinue }) {
  const { aiActorValue, humanActorValue, durationField, groupByField, correctActions, domain, label } = mapping

  const actorTypeValues = useMemo(() => uniqueValuesAtField(fileInfo.events, 'actor_type'), [fileInfo])
  const numericFields = useMemo(
    () => fileInfo.fields.filter((f) => isNumericField(fileInfo.events, f)),
    [fileInfo],
  )
  const humanActionValues = useMemo(() => {
    if (!humanActorValue) return []
    return uniqueValuesAtField(fileInfo.events.filter((e) => e.actor_type === humanActorValue), HUMAN_ACTION_FIELD)
  }, [fileInfo, humanActorValue])
  const pairs = useMemo(
    () => pairInteractions(fileInfo.events, aiActorValue, humanActorValue),
    [fileInfo, aiActorValue, humanActorValue],
  )
  const previewPairs = pairs.slice(0, 3)

  const domainValid = DOMAIN_RE.test(domain)
  const canContinue = aiActorValue && humanActorValue && durationField && domainValid && label.trim() && correctActions.length > 0

  function toggleCorrect(val) {
    setMapping((m) => ({
      ...m,
      correctActions: m.correctActions.includes(val) ? m.correctActions.filter((x) => x !== val) : [...m.correctActions, val],
    }))
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className={LABEL}>AI actor value</label>
          <select value={aiActorValue} onChange={(e) => setMapping((m) => ({ ...m, aiActorValue: e.target.value }))} className={INPUT}>
            <option value="">Choose…</option>
            {actorTypeValues.map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div>
          <label className={LABEL}>Human actor value</label>
          <select value={humanActorValue} onChange={(e) => setMapping((m) => ({ ...m, humanActorValue: e.target.value, correctActions: [] }))} className={INPUT}>
            <option value="">Choose…</option>
            {actorTypeValues.map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div>
          <label className={LABEL}>Response time field</label>
          <select value={durationField} onChange={(e) => setMapping((m) => ({ ...m, durationField: e.target.value }))} className={INPUT}>
            <option value="">Choose…</option>
            {numericFields.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div>
          <label className={LABEL}>Operator group field</label>
          <select value={groupByField} onChange={(e) => setMapping((m) => ({ ...m, groupByField: e.target.value }))} className={INPUT}>
            <option value="">None</option>
            {fileInfo.fields.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className={LABEL}>Correct outcomes</label>
        <p className="mb-1.5 text-xs text-gray-400">Check which human decisions mean the AI's suggestion was accepted / correct.</p>
        {humanActionValues.length === 0 ? (
          <p className="text-xs text-gray-400">Choose a human actor value above first.</p>
        ) : (
          <div className="space-y-1">
            {humanActionValues.map((val) => (
              <label key={val} className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox" checked={correctActions.includes(val)} onChange={() => toggleCorrect(val)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-300"
                />
                {val}
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className={LABEL}>Preview: first 3 mapped interaction pairs</label>
        {previewPairs.length === 0 ? (
          <p className="text-xs text-gray-400">Choose AI and human actor values above to preview the mapping.</p>
        ) : (
          <div className="overflow-x-auto rounded-md border border-gray-200">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-2 py-1.5 text-left font-medium">#</th>
                  <th className="px-2 py-1.5 text-left font-medium">AI action</th>
                  <th className="px-2 py-1.5 text-left font-medium">Human action</th>
                  <th className="px-2 py-1.5 text-left font-medium">Duration</th>
                  <th className="px-2 py-1.5 text-left font-medium">Correct</th>
                </tr>
              </thead>
              <tbody>
                {previewPairs.map((p, i) => {
                  const aiVal = getPath(p.aiEvent, AI_ACTION_FIELD)
                  const humanVal = getPath(p.humanEvent, HUMAN_ACTION_FIELD)
                  const dur = durationField ? getPath(p.humanEvent, durationField) : null
                  const correct = correctActions.includes(humanVal)
                  return (
                    <tr key={i} className="border-t border-gray-100 text-gray-700">
                      <td className="px-2 py-1.5">{i + 1}</td>
                      <td className="px-2 py-1.5">{String(aiVal)}</td>
                      <td className="px-2 py-1.5">{String(humanVal)}</td>
                      <td className="px-2 py-1.5">{typeof dur === 'number' ? `${dur.toFixed(1)}s` : '—'}</td>
                      <td className="px-2 py-1.5">{correct ? <span className="text-green-600">✓</span> : <span className="text-gray-300">✗</span>}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        {pairs.length > 0 && <p className="mt-1 text-xs text-gray-400">{pairs.length} interaction pair(s) matched in total.</p>}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className={LABEL}>Name this domain</label>
          <input
            type="text" value={domain} onChange={(e) => setMapping((m) => ({ ...m, domain: e.target.value }))}
            placeholder="e.g. my_healthcare_pilot" className={INPUT}
          />
          {domain && !domainValid && (
            <p className="mt-1 text-xs text-red-600">Lowercase letters, numbers, and underscores only - must start with a letter.</p>
          )}
        </div>
        <div>
          <label className={LABEL}>Display name</label>
          <input
            type="text" value={label} onChange={(e) => setMapping((m) => ({ ...m, label: e.target.value }))}
            placeholder="e.g. Healthcare — CT Triage" className={INPUT}
          />
        </div>
      </div>

      <div className="flex items-center gap-2 pt-1">
        <button type="button" onClick={onBack} className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50">
          <ChevronLeft size={12} /> Back
        </button>
        <button
          type="button" disabled={!canContinue} onClick={() => onContinue(pairs.length)}
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          Continue <ChevronRight size={12} />
        </button>
      </div>
    </div>
  )
}

// ── Stage 3: Fit & simulate ──────────────────────────────────────────────

function FitAndSimulateStage({ fileInfo, mapping, nValidPairs, configurationId, ontology, onBack, onSuccess }) {
  const { aiActorValue, humanActorValue, durationField, groupByField, correctActions, domain, label } = mapping

  const [persona, setPersona] = useState('aggregate')
  const [nSessions, setNSessions] = useState(10)
  const [nItems, setNItems] = useState(50)
  const [phase, setPhase] = useState(null) // null | 'fitting' | 'generating'
  const [sessionsDone, setSessionsDone] = useState(0)
  const [fitResult, setFitResult] = useState(null)
  const [simResult, setSimResult] = useState(null)

  const fitMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData()
      fd.append('file', fileInfo.file)
      fd.append('domain', domain)
      fd.append('label', label)
      fd.append('ai_actor_value', aiActorValue)
      fd.append('human_actor_value', humanActorValue)
      fd.append('duration_field', durationField)
      fd.append('group_by_field', groupByField || '')
      fd.append('accept_actions', JSON.stringify(correctActions))
      return api.ontology.fitModel(fd)
    },
  })

  const simMutation = useMutation({
    mutationFn: (body) => api.simulate.runProbabilistic(body),
  })

  async function handleFitAndSimulate() {
    setFitResult(null)
    setSimResult(null)
    setPhase('fitting')
    setSessionsDone(0)
    let progressTimer = null
    try {
      const fit = await fitMutation.mutateAsync()
      setFitResult(fit)
      setPhase('generating')

      // The backend doesn't stream real per-session progress over a single
      // POST, so this bar is a client-side estimate that advances toward
      // nSessions over a rough time budget while the request is in flight,
      // then snaps to 100% on the real response.
      const n = Math.max(1, Number(nSessions) || 1)
      const totalMs = n * 150
      const stepMs = Math.max(80, totalMs / Math.max(1, n - 1))
      let tick = 0
      progressTimer = setInterval(() => {
        tick += 1
        setSessionsDone((d) => Math.min(d + 1, n - 1))
        if (tick >= n - 1) clearInterval(progressTimer)
      }, stepMs)

      const sim = await simMutation.mutateAsync({
        name: `${domain}_byod_run`,
        configuration_id: Number(configurationId),
        domain,
        surrogate_tier: 1,
        n_items: Number(nItems),
        n_sessions: n,
        persona,
        fitted_model: fit.model_path,
        metrics: ['Tr', 'HCL', 'F', 'S'],
        pilot_tag: 'surrogate_probabilistic',
        app_version: 'sim_v2.0.0',
        ai_model_version: 'markov-1.0',
        seed: 42,
      })
      setSessionsDone(n)
      setSimResult(sim)
      onSuccess?.(sim)
    } catch {
      // surfaced below via fitMutation.error / simMutation.error
    } finally {
      if (progressTimer) clearInterval(progressTimer)
      setPhase(null)
    }
  }

  const busy = fitMutation.isPending || simMutation.isPending
  const error = fitMutation.error || simMutation.error
  const hasConfig = configurationId !== '' && configurationId != null

  return (
    <div className="space-y-4">
      <div className="space-y-1 rounded-md border border-gray-200 bg-gray-50 p-3 text-xs text-gray-600">
        <p><span className="font-medium text-gray-700">Domain:</span> {domain}</p>
        <p><span className="font-medium text-gray-700">Records:</span> {nValidPairs} interaction pair(s)</p>
        <p><span className="font-medium text-gray-700">AI actor:</span> "{aiActorValue}" &middot; <span className="font-medium text-gray-700">Human actor:</span> "{humanActorValue}"</p>
        <p><span className="font-medium text-gray-700">Correct outcomes:</span> {correctActions.join(', ')}</p>
        <p><span className="font-medium text-gray-700">Operator grouping:</span> {groupByField || 'none'}</p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <label className={LABEL}>Persona</label>
          <select value={persona} onChange={(e) => setPersona(e.target.value)} className={INPUT} disabled={busy}>
            <option value="aggregate">Average operator (fitted)</option>
            {(ontology?.persona_archetypes ?? []).map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
          </select>
        </div>
        <div>
          <label className={LABEL}>Sessions to generate</label>
          <input type="number" min={1} value={nSessions} onChange={(e) => setNSessions(e.target.value)} className={INPUT} disabled={busy} />
        </div>
        <div>
          <label className={LABEL}>Items per session</label>
          <input type="number" min={1} value={nItems} onChange={(e) => setNItems(e.target.value)} className={INPUT} disabled={busy} />
        </div>
      </div>

      <p className="rounded-md border border-indigo-100 bg-indigo-50 p-2.5 text-xs text-indigo-800">
        We will fit a probability model from your {nValidPairs} records, then use it to generate {nSessions || 0} simulated
        session{Number(nSessions) === 1 ? '' : 's'} of {nItems || 0} interactions each. This usually takes under 10 seconds.
      </p>

      {!phase && !simResult && (
        <div className="space-y-1">
          <button
            type="button" disabled={busy || !hasConfig} onClick={handleFitAndSimulate}
            className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
          >
            Fit model and simulate <ChevronRight size={14} />
          </button>
          {!hasConfig && <p className="text-xs text-gray-400">Pick a target configuration above first.</p>}
        </div>
      )}

      {phase === 'fitting' && (
        <div className="flex items-center gap-2 rounded-md border border-gray-200 bg-gray-50 p-3 text-sm text-gray-600">
          <Loader2 size={14} className="animate-spin" /> Fitting your surrogate model…
        </div>
      )}

      {phase === 'generating' && (
        <div className="space-y-2 rounded-md border border-gray-200 bg-gray-50 p-3">
          <p className="flex items-center gap-2 text-sm text-gray-600">
            <Loader2 size={14} className="animate-spin" /> Generating {nSessions} session{Number(nSessions) === 1 ? '' : 's'}…
          </p>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-indigo-500 transition-all"
              style={{ width: `${Math.min(100, (sessionsDone / Math.max(1, Number(nSessions) || 1)) * 100)}%` }}
            />
          </div>
        </div>
      )}

      {fitResult && (
        <div className="space-y-1 rounded-md border border-green-200 bg-green-50 p-3 text-xs text-green-800">
          <p className="flex items-center gap-1.5"><CheckCircle2 size={12} /> Model fitted on {fitResult.n_sessions_fitted} sessions</p>
          <p className="flex items-center gap-1.5"><CheckCircle2 size={12} /> AI actions: {fitResult.ai_actions.join(', ')}</p>
          <p className="flex items-center gap-1.5"><CheckCircle2 size={12} /> Empirical accept rate: {(fitResult.aggregate_tr * 100).toFixed(1)}%</p>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {friendlyError(error)}
        </div>
      )}

      {simResult && (
        <div className="space-y-1.5 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          <p className="flex items-center gap-1.5 font-medium">
            <CheckCircle2 size={14} /> Generated {simResult.n_sessions_generated} session(s) &middot; {simResult.n_decisions_total} decisions
          </p>
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <Link to={`/config/${configurationId}/results`} className="inline-flex items-center gap-0.5 font-medium text-green-800 underline hover:text-green-900">
              View in dashboard <ChevronRight size={12} />
            </Link>
            <Link to="/compare" className="inline-flex items-center gap-0.5 font-medium text-green-800 underline hover:text-green-900">
              Compare versions <ChevronRight size={12} />
            </Link>
          </div>
          <p className="text-xs text-green-800">
            Your domain "{domain}" has been saved. It will appear as a template next time you open Simulate.
          </p>
        </div>
      )}

      <div className="pt-1">
        <button
          type="button" disabled={busy} onClick={onBack}
          className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-50"
        >
          <ChevronLeft size={12} /> Back
        </button>
      </div>
    </div>
  )
}

// ── Stage card shell ─────────────────────────────────────────────────────

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

function StepBreadcrumb({ stage }) {
  const steps = ['Upload', 'Map fields', 'Fit & simulate']
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

// ── Main component ───────────────────────────────────────────────────────

export default function FitAndSimulateFlow({ configurationId, ontology, onSuccess }) {
  const [stage, setStage] = useState(1)
  const [fileInfo, setFileInfo] = useState(null)
  const [nValidPairs, setNValidPairs] = useState(0)
  const [mapping, setMapping] = useState({
    aiActorValue: '', humanActorValue: '', durationField: '', groupByField: '',
    correctActions: [], domain: '', label: '',
  })

  return (
    <div className="space-y-3">
      <StepBreadcrumb stage={stage} />

      <StageCard
        index={1} stage={stage} title="Upload"
        summary={fileInfo ? `${fileInfo.fileName} · ${fileInfo.recordCount} records` : null}
      >
        <UploadStage onContinue={(info) => { setFileInfo(info); setStage(2) }} />
      </StageCard>

      {fileInfo && (
        <StageCard
          index={2} stage={stage} title="Map fields"
          summary={stage > 2 ? `${mapping.domain} · ${nValidPairs} pairs mapped` : null}
        >
          <MapFieldsStage
            fileInfo={fileInfo}
            mapping={mapping}
            setMapping={setMapping}
            onBack={() => setStage(1)}
            onContinue={(pairCount) => { setNValidPairs(pairCount); setStage(3) }}
          />
        </StageCard>
      )}

      {fileInfo && stage >= 3 && (
        <StageCard index={3} stage={stage} title="Fit & simulate">
          <FitAndSimulateStage
            fileInfo={fileInfo}
            mapping={mapping}
            nValidPairs={nValidPairs}
            configurationId={configurationId}
            ontology={ontology}
            onBack={() => setStage(2)}
            onSuccess={onSuccess}
          />
        </StageCard>
      )}
    </div>
  )
}
