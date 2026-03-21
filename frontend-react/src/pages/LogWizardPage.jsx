import { useState, useRef, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Upload, Link2, ChevronRight, CheckCircle2,
  AlertTriangle, Loader2, FileJson, X, FlaskConical,
  Settings2,
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

// ── Step indicators ───────────────────────────────────────────

function StepDots({ current }) {
  const steps = ['Select Config', 'Pilot Setup', 'Upload Logs', 'Evaluate']
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

  function handleNext() {
    const id = Number(selectedId)
    const cfg = configs?.find(c => c.id === id) ?? null
    onNext(id, cfg)
  }

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
        onClick={handleNext}
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

// ── Step 1 (Pilot Setup) helpers ──────────────────────────────

const DEFAULT_MAPPING = {
  actor_type_field:  'actor_type',
  human_value:       'human',
  ai_value:          'ai',
  latency_field:     'latency_ms',
  latency_unit:      'ms',
  duration_field:    'duration_s',
  duration_unit:     's',
  correct_field:     'correct',
  correct_value:     'true',
  incorrect_value:   'false',
  ai_action_names:    ['ai_evaluated'],
  human_action_names: ['application_created', 'operator_verified'],
  package_format:    'single_json',
}

function UnitToggle({ value, onChange }) {
  return (
    <div className="flex items-center bg-gray-100 rounded p-0.5">
      {['ms', 's'].map(u => (
        <button
          key={u}
          type="button"
          onClick={() => onChange(u)}
          className={clsx(
            'px-2 py-0.5 text-xs rounded font-medium transition-colors',
            value === u
              ? 'bg-white shadow-sm text-gray-800'
              : 'text-gray-500 hover:text-gray-700',
          )}
        >
          {u}
        </button>
      ))}
    </div>
  )
}

function ChipInput({ values, onChange, placeholder }) {
  const [input, setInput] = useState('')

  function add() {
    const v = input.trim()
    if (v && !values.includes(v)) onChange([...values, v])
    setInput('')
  }
  function handleKey(e) {
    if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add() }
  }

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap gap-1.5">
        {values.map(v => (
          <span
            key={v}
            className="flex items-center gap-1 px-2 py-0.5 rounded-full
                       bg-indigo-100 text-indigo-700 text-xs font-mono"
          >
            {v}
            <button
              type="button"
              onClick={() => onChange(values.filter(x => x !== v))}
              className="hover:text-indigo-900"
            >
              <X size={10} />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={placeholder}
          className="flex-1 border border-gray-200 rounded-md px-3 py-1.5 text-xs font-mono
                     text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button
          type="button"
          onClick={add}
          className="px-2.5 py-1.5 text-xs rounded-md border border-gray-200
                     text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Add
        </button>
      </div>
    </div>
  )
}

function FieldRow({ label, note, children }) {
  return (
    <div className="grid grid-cols-5 gap-3 items-start py-2.5 border-b border-gray-100 last:border-0">
      <div className="col-span-2">
        <p className="text-xs font-medium text-gray-700">{label}</p>
        {note && <p className="text-xs text-gray-400 mt-0.5">{note}</p>}
      </div>
      <div className="col-span-3">{children}</div>
    </div>
  )
}

function TestMappingPanel({ pilotTag }) {
  const [open, setOpen] = useState(false)
  const [sampleJson, setSampleJson] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function runTest() {
    setLoading(true); setError(null); setResult(null)
    try {
      const parsed = JSON.parse(sampleJson)
      const res = await api.adapters.test({ pilot_tag: pilotTag, sample_event: parsed })
      setResult(res)
    } catch (e) {
      setError(e instanceof SyntaxError ? `Invalid JSON — ${e.message}` : e.message)
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 text-xs text-indigo-600
                   hover:text-indigo-800 transition-colors"
      >
        <FlaskConical size={12} /> Test mapping with a sample event
      </button>
    )
  }

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-gray-600 flex items-center gap-1.5">
          <FlaskConical size={12} className="text-indigo-500" /> Test Field Mapping
        </p>
        <button
          type="button"
          onClick={() => { setOpen(false); setResult(null); setError(null) }}
          className="text-gray-400 hover:text-gray-600"
        >
          <X size={13} />
        </button>
      </div>
      <p className="text-xs text-gray-500">
        Paste a single raw event dict. See how it maps to canonical
        DecisionEvent fields with the current adapter config.
      </p>
      <textarea
        value={sampleJson}
        onChange={e => setSampleJson(e.target.value)}
        placeholder={'{"event_type": "ai_evaluated", "latency_ms": 120, "actor_type": "ai", ...}'}
        className="w-full font-mono text-xs border border-gray-200 rounded-md p-2
                   focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none bg-white"
        rows={4}
      />
      <button
        type="button"
        disabled={!sampleJson.trim() || loading}
        onClick={runTest}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium
                   bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading
          ? <><Loader2 size={11} className="animate-spin" /> Testing…</>
          : 'Run Test'}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {result && (
        <div className="space-y-2">
          {result.warning && (
            <p className="text-xs text-amber-600">{result.warning}</p>
          )}
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">DecisionEvent:</p>
            <pre className="text-xs font-mono bg-white rounded border border-gray-200
                            p-2 overflow-auto max-h-40 text-gray-700">
              {JSON.stringify(result.decision_event ?? result.mapped, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

function MappingForm({ pilotTag, initial, onSubmit, onSkip, onBack, submitting, submitError }) {
  const [form, setForm] = useState({ ...DEFAULT_MAPPING, ...initial })
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({ ...form, pilot_tag: pilotTag })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Info banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
        Map your log field names to the canonical fields the HAIC engine expects.
        Defaults match the standard <span className="font-mono">applications</span> pilot —
        most setups can click <strong>Register mapping</strong> unchanged.
      </div>

      {/* Fields table */}
      <div className="bg-white rounded-lg border border-gray-200 px-4">

        <FieldRow label="Actor type field" note="field that holds 'human' / 'ai' label">
          <input
            type="text" value={form.actor_type_field}
            onChange={e => set('actor_type_field', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="Human value" note="value that means human actor">
          <input
            type="text" value={form.human_value}
            onChange={e => set('human_value', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="AI value" note="value that means AI actor">
          <input
            type="text" value={form.ai_value}
            onChange={e => set('ai_value', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="AI response latency" note="field + unit">
          <div className="flex gap-2 items-center">
            <input
              type="text" value={form.latency_field}
              onChange={e => set('latency_field', e.target.value)}
              className="flex-1 border border-gray-200 rounded px-2 py-1 text-xs font-mono
                         focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <UnitToggle value={form.latency_unit} onChange={v => set('latency_unit', v)} />
          </div>
        </FieldRow>

        <FieldRow label="Human decision time" note="field + unit">
          <div className="flex gap-2 items-center">
            <input
              type="text" value={form.duration_field}
              onChange={e => set('duration_field', e.target.value)}
              className="flex-1 border border-gray-200 rounded px-2 py-1 text-xs font-mono
                         focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <UnitToggle value={form.duration_unit} onChange={v => set('duration_unit', v)} />
          </div>
        </FieldRow>

        <FieldRow label="Correct/incorrect field" note="boolean or string outcome field">
          <input
            type="text" value={form.correct_field}
            onChange={e => set('correct_field', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="Correct value" note='string meaning "correct"'>
          <input
            type="text" value={form.correct_value}
            onChange={e => set('correct_value', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="Incorrect value" note='string meaning "incorrect"'>
          <input
            type="text" value={form.incorrect_value}
            onChange={e => set('incorrect_value', e.target.value)}
            className="w-full border border-gray-200 rounded px-2 py-1 text-xs font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </FieldRow>

        <FieldRow label="AI action names" note="event_type values owned by AI">
          <ChipInput
            values={form.ai_action_names}
            onChange={v => set('ai_action_names', v)}
            placeholder="e.g. ai_evaluated"
          />
        </FieldRow>

        <FieldRow label="Human action names" note="event_type values owned by human">
          <ChipInput
            values={form.human_action_names}
            onChange={v => set('human_action_names', v)}
            placeholder="e.g. operator_verified"
          />
        </FieldRow>

        <FieldRow label="File packaging" note="how log files are submitted">
          <div className="flex gap-4">
            {[
              ['single_json', 'Single JSON file'],
              ['zip',         'ZIP of files'],
              ['folder',      'Folder'],
            ].map(([v, label]) => (
              <label key={v} className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio" name="pkg_format" value={v}
                  checked={form.package_format === v}
                  onChange={() => set('package_format', v)}
                  className="text-indigo-600 focus:ring-indigo-300"
                />
                <span className="text-xs text-gray-700">{label}</span>
              </label>
            ))}
          </div>
        </FieldRow>
      </div>

      {submitError && (
        <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-xs text-red-700">
          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
          {submitError}
        </div>
      )}

      <div className="flex items-center gap-3 flex-wrap">
        <button
          type="button" onClick={onBack}
          className="px-4 py-2 rounded-md text-sm font-medium border border-gray-200
                     text-gray-600 hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          type="submit" disabled={submitting}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                     bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {submitting
            ? <><Loader2 size={13} className="animate-spin" /> Registering…</>
            : 'Register mapping'}
        </button>
        <button
          type="button" onClick={onSkip}
          className="text-xs text-gray-400 hover:text-gray-600 transition-colors ml-2"
        >
          Skip — use generic adapter
        </button>
      </div>

      <TestMappingPanel pilotTag={pilotTag} />
    </form>
  )
}

function StepPilot({ configId, config, onNext, onBack }) {
  const pilotTag = (config?.application_name ?? 'generic').toLowerCase()

  const { data: adaptersData, isLoading: checking } = useQuery({
    queryKey: ['adapters'],
    queryFn: () => api.adapters.list(),
    staleTime: 0,
  })

  const adapterExists = adaptersData?.adapters?.some(a => a.tag === pilotTag)

  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [submitted, setSubmitted] = useState(false)

  async function handleSubmit(cfg) {
    setSubmitting(true); setSubmitError(null)
    try {
      await api.adapters.register(cfg)
      setSubmitted(true)
    } catch (e) {
      setSubmitError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (checking) {
    return (
      <div className="flex items-center gap-2 text-gray-400 text-sm py-10">
        <Loader2 size={15} className="animate-spin" /> Checking pilot adapter…
      </div>
    )
  }

  // ── Adapter exists, form not open ──
  if (adapterExists && !showForm && !submitted) {
    return (
      <div className="space-y-5 max-w-xl">
        <PilotLabel pilotTag={pilotTag} config={config} />
        <div className="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4">
          <CheckCircle2 size={18} className="text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-green-800">
              ✓ {config?.application_name} — field mapping configured
            </p>
            <p className="text-xs text-green-600 mt-0.5">
              Adapter registered for pilot tag <span className="font-mono">{pilotTag}</span>.
            </p>
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
            onClick={() => onNext({ skipped: false })}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                       bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            Continue <ChevronRight size={14} />
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 ml-2"
          >
            <Settings2 size={12} /> Reconfigure
          </button>
        </div>
        <TestMappingPanel pilotTag={pilotTag} />
      </div>
    )
  }

  // ── Submitted successfully ──
  if (submitted) {
    return (
      <div className="space-y-5 max-w-xl">
        <PilotLabel pilotTag={pilotTag} config={config} />
        <div className="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4">
          <CheckCircle2 size={18} className="text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-green-800">Adapter registered successfully</p>
            <p className="text-xs text-green-600 mt-0.5">
              Field mapping saved for pilot tag <span className="font-mono">{pilotTag}</span>.
            </p>
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
            onClick={() => onNext({ skipped: false })}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                       bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            Continue <ChevronRight size={14} />
          </button>
        </div>
      </div>
    )
  }

  // ── Show mapping form ──
  return (
    <div className="space-y-5 max-w-xl">
      <PilotLabel pilotTag={pilotTag} config={config} />
      <MappingForm
        pilotTag={pilotTag}
        initial={{}}
        onSubmit={handleSubmit}
        onSkip={() => onNext({ skipped: true })}
        onBack={onBack}
        submitting={submitting}
        submitError={submitError}
      />
    </div>
  )
}

function PilotLabel({ pilotTag, config }) {
  return (
    <p className="text-xs text-gray-400">
      Pilot:{' '}
      <span className="font-mono text-gray-600">{pilotTag}</span>
      {config?.application_name && (
        <span className="text-gray-400"> · {config.application_name}</span>
      )}
    </p>
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

function Step2({ configId, onNext, onBack, skippedSetup }) {
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

      {/* Generic-adapter warning */}
      {skippedSetup && (
        <div className="flex items-start gap-2 rounded-md bg-amber-50 border border-amber-200 p-3 text-xs text-amber-700">
          <AlertTriangle size={13} className="mt-0.5 flex-shrink-0" />
          <span>
            Using generic field mapping — some metrics may not compute correctly.
            {' '}
            <button
              onClick={onBack}
              className="underline font-medium hover:text-amber-900"
            >
              Complete pilot setup
            </button>
            {' '}to improve results.
          </span>
        </div>
      )}

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
  const [config, setConfig] = useState(null)
  const [skippedSetup, setSkippedSetup] = useState(false)

  return (
    <div className="max-w-2xl space-y-2">
      <h1 className="text-base font-semibold text-gray-900">Log Ingest Wizard</h1>
      <p className="text-xs text-gray-400 mb-6">
        Select a configuration, set up field mapping, ingest your logs, then trigger evaluation.
      </p>

      <StepDots current={step} />

      {/* Step 0 — select configuration */}
      {step === 0 && (
        <Step1
          onNext={(id, cfg) => { setConfigId(id); setConfig(cfg ?? null); setStep(1) }}
        />
      )}

      {/* Step 1 — pilot adapter setup */}
      {step === 1 && (
        <StepPilot
          configId={configId}
          config={config}
          onNext={({ skipped }) => { setSkippedSetup(skipped); setStep(2) }}
          onBack={() => setStep(0)}
        />
      )}

      {/* Step 2 — upload / register logs */}
      {step === 2 && (
        <Step2
          configId={configId}
          skippedSetup={skippedSetup}
          onNext={() => setStep(3)}
          onBack={() => setStep(1)}
        />
      )}

      {/* Step 3 — trigger evaluation */}
      {step === 3 && (
        <Step3
          configId={configId}
          onBack={() => setStep(2)}
        />
      )}
    </div>
  )
}
