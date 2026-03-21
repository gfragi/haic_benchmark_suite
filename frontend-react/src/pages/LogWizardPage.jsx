import { useState, useRef, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Upload, Link2, ChevronRight, CheckCircle2,
  AlertTriangle, Loader2, FileJson, X,
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

// ── Step indicators ───────────────────────────────────────────

function StepDots({ current }) {
  const steps = ['Select Config', 'Upload Logs', 'Evaluate']
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((label, i) => {
        const done = i < current
        const active = i === current
        return (
          <div key={i} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div className={clsx(
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-colors',
                done  ? 'bg-indigo-600 text-white'
                      : active ? 'bg-indigo-100 text-indigo-700 ring-2 ring-indigo-500'
                      : 'bg-gray-100 text-gray-400',
              )}>
                {done ? <CheckCircle2 size={14} /> : i + 1}
              </div>
              <span className={clsx(
                'text-xs whitespace-nowrap',
                active ? 'text-indigo-700 font-medium' : 'text-gray-400',
              )}>{label}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={clsx(
                'h-px w-16 mx-1 mb-5 transition-colors',
                done ? 'bg-indigo-400' : 'bg-gray-200',
              )} />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Step 1: Select Config ─────────────────────────────────────

function Step1({ onNext }) {
  const [selectedId, setSelectedId] = useState('')
  const { data: configs, isLoading, error } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  if (isLoading) return (
    <div className="flex items-center gap-2 text-gray-400 text-sm py-10">
      <Loader2 size={15} className="animate-spin" /> Loading configurations…
    </div>
  )
  if (error) return (
    <div className="text-red-600 text-sm py-4">{error.message}</div>
  )

  const options = configs ?? []

  return (
    <div className="space-y-4 max-w-md">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Configuration
        </label>
        <select
          value={selectedId}
          onChange={e => setSelectedId(e.target.value)}
          className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700
                     focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
        >
          <option value="">— Select a configuration —</option>
          {options.map(c => (
            <option key={c.id} value={c.id}>
              #{c.id} · {c.application_name}
              {c.ai_model_name ? ` (${c.ai_model_name})` : ''}
            </option>
          ))}
        </select>
      </div>
      <button
        disabled={!selectedId}
        onClick={() => onNext(Number(selectedId))}
        className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                   bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Next <ChevronRight size={14} />
      </button>
    </div>
  )
}

// ── Checklist ────────────────────────────────────────────────

const CHECKLIST = [
  {
    id: 'actor_type',
    label: 'actor_type field on all events',
    note: 'required for any metrics',
    keywords: ['actor_type', 'actor'],
  },
  {
    id: 'correct',
    label: 'correct field on operator events',
    note: 'required for Tr (Trust)',
    keywords: ['correct'],
  },
  {
    id: 'duration',
    label: 'duration_s or latency_ms on events',
    note: 'required for HCL and D',
    keywords: ['duration', 'latency'],
  },
  {
    id: 'baseline_s',
    label: 'baseline_s in session header',
    note: 'required for EL (Effort Loss)',
    keywords: ['baseline'],
  },
]

// Returns true if the item has NO matching warning (i.e. it's satisfied)
function isItemSatisfied(item, rawWarnings) {
  const texts = rawWarnings.map(w =>
    typeof w === 'string' ? w.toLowerCase() : `${w.metric ?? ''} ${w.warning ?? ''}`.toLowerCase()
  )
  return !item.keywords.some(kw => texts.some(t => t.includes(kw)))
}

function ChecklistGate({ onConfirm, onBack, configId, config }) {
  const [checked, setChecked] = useState({})
  const allChecked = CHECKLIST.every(item => checked[item.id])

  function toggle(id) {
    setChecked(c => ({ ...c, [id]: !c[id] }))
  }

  return (
    <div className="space-y-5 max-w-xl">
      <p className="text-xs text-gray-400">
        Config: <span className="font-medium text-gray-600">
          #{configId}{config?.application_name ? ` · ${config.application_name}` : ''}
        </span>
      </p>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
        <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide">
          Pre-upload checklist
        </p>
        <p className="text-xs text-amber-600">
          Confirm your log file includes these fields for accurate metric computation.
        </p>
        <div className="space-y-2.5">
          {CHECKLIST.map(item => (
            <label key={item.id} className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={!!checked[item.id]}
                onChange={() => toggle(item.id)}
                className="mt-0.5 rounded border-amber-300 text-indigo-600 focus:ring-indigo-300"
              />
              <div>
                <p className="text-sm font-mono font-medium text-gray-800">{item.label}</p>
                <p className="text-xs text-gray-500">{item.note}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md text-sm font-medium border border-gray-200
                     text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          disabled={!allChecked}
          onClick={onConfirm}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                     bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Confirmed — proceed to upload <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

// ── Drop zone ─────────────────────────────────────────────────

function DropZone({ onFile, disabled }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = useCallback(e => {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const file = e.dataTransfer.files?.[0]
    if (file) onFile(file)
  }, [onFile, disabled])

  return (
    <div
      onDragEnter={e => { e.preventDefault(); setDragging(true) }}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={clsx(
        'border-2 border-dashed rounded-lg p-8 flex flex-col items-center gap-3 cursor-pointer transition-colors',
        dragging && !disabled ? 'border-indigo-400 bg-indigo-50'
          : disabled ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-60'
          : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50',
      )}
    >
      <FileJson size={28} className="text-gray-300" />
      <div className="text-center">
        <p className="text-sm font-medium text-gray-600">Drop JSON log file here</p>
        <p className="text-xs text-gray-400 mt-0.5">or click to browse</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".json,application/json"
        className="hidden"
        onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f) }}
      />
    </div>
  )
}

// ── Step 2: Upload / Register ─────────────────────────────────

function Step2({ configId, onNext, onBack }) {
  const [checklistConfirmed, setChecklistConfirmed] = useState(false)
  const [tab, setTab] = useState('upload')   // 'upload' | 'endpoint'
  const [file, setFile] = useState(null)
  const [endpoint, setEndpoint] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState(null)

  const { data: config } = useQuery({
    queryKey: ['config', configId],
    queryFn: () => api.configs.get(configId),
  })

  if (!checklistConfirmed) {
    return (
      <ChecklistGate
        configId={configId}
        config={config}
        onConfirm={() => setChecklistConfirmed(true)}
        onBack={onBack}
      />
    )
  }

  async function handleUpload() {
    if (!file) return
    setUploading(true)
    setError(null)
    setUploadResult(null)
    try {
      const result = await api.logs.upload(configId, file)
      setUploadResult(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleRegister() {
    if (!endpoint.trim()) return
    setUploading(true)
    setError(null)
    setUploadResult(null)
    try {
      const result = await api.logs.register(configId, { endpoint_url: endpoint.trim() })
      setUploadResult(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  // Normalize: upload returns schema_warnings (string[]), register returns validation_warnings ({metric,warning}[])
  const rawWarnings = uploadResult?.schema_warnings ?? uploadResult?.validation_warnings ?? []
  const canProceed = uploadResult != null

  return (
    <div className="space-y-5 max-w-xl">
      {/* Config label */}
      <p className="text-xs text-gray-400">
        Config: <span className="font-medium text-gray-600">
          #{configId}{config?.application_name ? ` · ${config.application_name}` : ''}
        </span>
      </p>

      {/* Tab toggle */}
      <div className="flex items-center bg-gray-100 rounded-lg p-1 gap-0.5 w-fit">
        {[['upload', 'Upload File'], ['endpoint', 'Register Endpoint']].map(([v, label]) => (
          <button
            key={v}
            onClick={() => { setTab(v); setUploadResult(null); setError(null) }}
            className={clsx(
              'px-4 py-1.5 text-sm rounded-md font-medium transition-colors',
              tab === v ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700',
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Upload tab */}
      {tab === 'upload' && (
        <div className="space-y-3">
          {!uploadResult ? (
            <>
              <DropZone onFile={setFile} disabled={uploading} />
              {file && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <FileJson size={14} className="text-indigo-500" />
                  <span className="font-medium">{file.name}</span>
                  <span className="text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
                  <button onClick={() => setFile(null)} className="ml-auto text-gray-300 hover:text-gray-500">
                    <X size={13} />
                  </button>
                </div>
              )}
              <button
                disabled={!file || uploading}
                onClick={handleUpload}
                className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                           bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                           disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {uploading
                  ? <><Loader2 size={13} className="animate-spin" /> Uploading…</>
                  : <><Upload size={13} /> Upload</>}
              </button>
            </>
          ) : (
            <UploadSummary
              result={uploadResult}
              rawWarnings={rawWarnings}
              onReset={() => { setUploadResult(null); setFile(null) }}
            />
          )}
        </div>
      )}

      {/* Endpoint tab */}
      {tab === 'endpoint' && (
        <div className="space-y-3">
          {!uploadResult ? (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Log endpoint URL
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Link2 size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="url"
                      placeholder="https://your-service.com/logs"
                      value={endpoint}
                      onChange={e => setEndpoint(e.target.value)}
                      className="w-full border border-gray-200 rounded-md pl-8 pr-3 py-2 text-sm
                                 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    />
                  </div>
                  <button
                    disabled={!endpoint.trim() || uploading}
                    onClick={handleRegister}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                               bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                               disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
                  >
                    {uploading
                      ? <><Loader2 size={13} className="animate-spin" /> Registering…</>
                      : 'Register'}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <UploadSummary
              result={uploadResult}
              rawWarnings={rawWarnings}
              onReset={() => { setUploadResult(null); setEndpoint('') }}
            />
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-red-700 text-sm">
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Nav buttons */}
      <div className="flex items-center gap-3 pt-1">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md text-sm font-medium border border-gray-200
                     text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          disabled={!canProceed}
          onClick={onNext}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                     bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continue to Evaluate <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

// ── Upload summary + warnings ─────────────────────────────────

function warningText(w) {
  return typeof w === 'string' ? w : `${w.metric ? w.metric + ': ' : ''}${w.warning ?? JSON.stringify(w)}`
}

function UploadSummary({ result, rawWarnings, onReset }) {
  return (
    <div className="space-y-3">
      {/* Received banner */}
      <div className="flex items-center gap-2 rounded-md bg-green-50 border border-green-200 p-3 text-sm text-green-700">
        <CheckCircle2 size={15} className="flex-shrink-0" />
        <span>
          {result.event_count != null
            ? <>Received <span className="font-semibold">{result.event_count}</span> events</>
            : 'Log accepted'}
        </span>
        <button onClick={onReset} className="ml-auto text-green-400 hover:text-green-600">
          <X size={13} />
        </button>
      </div>

      {/* Checklist satisfaction */}
      <div className="rounded-md border border-gray-200 divide-y divide-gray-100 overflow-hidden">
        <p className="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
          Field coverage
        </p>
        {CHECKLIST.map(item => {
          const ok = isItemSatisfied(item, rawWarnings)
          return (
            <div key={item.id} className="flex items-center gap-2.5 px-3 py-2">
              {ok
                ? <CheckCircle2 size={13} className="text-green-500 flex-shrink-0" />
                : <AlertTriangle size={13} className="text-amber-500 flex-shrink-0" />}
              <div className="min-w-0">
                <p className={clsx('text-xs font-mono', ok ? 'text-gray-700' : 'text-amber-700')}>
                  {item.label}
                </p>
                {!ok && (
                  <p className="text-xs text-amber-500">{item.note}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Raw warnings */}
      {rawWarnings.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-amber-600 uppercase tracking-wide">
            Schema warnings ({rawWarnings.length})
          </p>
          {rawWarnings.map((w, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-md bg-amber-50 border border-amber-200 p-2.5 text-xs text-amber-700"
            >
              <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
              <span>{warningText(w)}</span>
            </div>
          ))}
        </div>
      )}

      {rawWarnings.length === 0 && (
        <p className="text-xs text-gray-400">No schema warnings.</p>
      )}
    </div>
  )
}

// ── Step 3: Evaluate + Poll ───────────────────────────────────

function Step3({ configId, onBack }) {
  const navigate = useNavigate()
  const [phase, setPhase] = useState('idle')   // idle | triggering | polling | done | error
  const [errMsg, setErrMsg] = useState(null)
  const pollRef = useRef(null)

  // stop polling on unmount
  useEffect(() => () => clearInterval(pollRef.current), [])

  async function startEvaluation() {
    setPhase('triggering')
    setErrMsg(null)
    try {
      await api.evaluate.trigger(configId)
    } catch (e) {
      // some backends return 200 with body; ignore "no content" errors
      if (!e.message?.includes('JSON')) {
        setPhase('error')
        setErrMsg(e.message)
        return
      }
    }
    setPhase('polling')
    startPolling()
  }

  function startPolling() {
    let attempts = 0
    const MAX = 60   // 3 min cap

    pollRef.current = setInterval(async () => {
      attempts++
      if (attempts > MAX) {
        clearInterval(pollRef.current)
        setPhase('error')
        setErrMsg('Timed out waiting for results (3 min). The job may still be running.')
        return
      }
      try {
        const stubs = await api.results.list(configId)
        if (stubs && stubs.length > 0) {
          clearInterval(pollRef.current)
          setPhase('done')
        }
      } catch (e) {
        // 404 = no results yet — keep polling
        if (!e.message?.includes('No results found')) {
          clearInterval(pollRef.current)
          setPhase('error')
          setErrMsg(e.message)
        }
      }
    }, 3000)
  }

  const { data: config } = useQuery({
    queryKey: ['config', configId],
    queryFn: () => api.configs.get(configId),
  })

  return (
    <div className="space-y-6 max-w-lg">
      <p className="text-xs text-gray-400">
        Config: <span className="font-medium text-gray-600">
          #{configId}{config?.application_name ? ` · ${config.application_name}` : ''}
        </span>
      </p>

      {/* Idle: trigger button */}
      {phase === 'idle' && (
        <div className="rounded-lg border border-gray-200 bg-white p-6 flex flex-col items-center gap-4 text-center">
          <div className="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center">
            <ChevronRight size={22} className="text-indigo-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800">Ready to evaluate</p>
            <p className="text-xs text-gray-400 mt-0.5">
              Logs have been ingested. Start the evaluation pipeline.
            </p>
          </div>
          <button
            onClick={startEvaluation}
            className="px-5 py-2.5 rounded-md text-sm font-medium bg-indigo-600 text-white
                       hover:bg-indigo-700 transition-colors"
          >
            Trigger Evaluation
          </button>
        </div>
      )}

      {/* Triggering / Polling: spinner */}
      {(phase === 'triggering' || phase === 'polling') && (
        <div className="rounded-lg border border-indigo-100 bg-indigo-50 p-8 flex flex-col items-center gap-3">
          <Loader2 size={28} className="animate-spin text-indigo-500" />
          <p className="text-sm font-medium text-indigo-700">
            {phase === 'triggering' ? 'Starting evaluation…' : 'Computing metrics…'}
          </p>
          <p className="text-xs text-indigo-400">
            {phase === 'polling' ? 'Checking for results every 3 seconds' : ''}
          </p>
        </div>
      )}

      {/* Done */}
      {phase === 'done' && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-6 flex flex-col items-center gap-4 text-center">
          <CheckCircle2 size={32} className="text-green-500" />
          <div>
            <p className="text-sm font-semibold text-green-800">Evaluation complete!</p>
            <p className="text-xs text-green-600 mt-0.5">Results are ready to view.</p>
          </div>
          <button
            onClick={() => navigate(`/config/${configId}/results`)}
            className="px-5 py-2.5 rounded-md text-sm font-medium bg-green-600 text-white
                       hover:bg-green-700 transition-colors"
          >
            View Results
          </button>
        </div>
      )}

      {/* Error */}
      {phase === 'error' && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-5 space-y-3">
          <div className="flex items-start gap-2 text-red-700 text-sm">
            <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
            {errMsg}
          </div>
          <button
            onClick={() => { setPhase('idle'); setErrMsg(null) }}
            className="px-4 py-1.5 rounded-md text-xs font-medium border border-red-200
                       text-red-600 hover:bg-red-100 transition-colors"
          >
            Try again
          </button>
        </div>
      )}

      {/* Back (only from idle or error) */}
      {(phase === 'idle' || phase === 'error') && (
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md text-sm font-medium border border-gray-200
                     text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
      )}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────

export default function LogWizardPage() {
  const [step, setStep] = useState(0)
  const [configId, setConfigId] = useState(null)

  return (
    <div className="max-w-2xl space-y-2">
      <h1 className="text-base font-semibold text-gray-900">Log Ingest Wizard</h1>
      <p className="text-xs text-gray-400 mb-6">
        Select a configuration, ingest your logs, then trigger the evaluation pipeline.
      </p>

      <StepDots current={step} />

      {step === 0 && (
        <Step1
          onNext={id => { setConfigId(id); setStep(1) }}
        />
      )}
      {step === 1 && (
        <Step2
          configId={configId}
          onNext={() => setStep(2)}
          onBack={() => setStep(0)}
        />
      )}
      {step === 2 && (
        <Step3
          configId={configId}
          onBack={() => setStep(1)}
        />
      )}
    </div>
  )
}
