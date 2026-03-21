import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
  ChevronRight, ChevronLeft, CheckCircle2, XCircle,
  Download, Rocket, Plus, X,
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

// ── Constants ──────────────────────────────────────────────────────────────

const DOMAINS = ['Healthcare', 'Energy', 'Applications', 'Manufacturing', 'Smart Cities', 'Other']

const DOMAIN_EXAMPLES = [
  {
    domain: 'Healthcare',
    emoji: '🏥',
    example: 'AI diagnoses medical image → radiologist confirms without override',
    note: 'AI is correct when no corrective human event follows the AI decision.',
  },
  {
    domain: 'Energy',
    emoji: '⚡',
    example: 'AI predicts equipment fault → operator validates the alarm',
    note: 'Use an existing validated: true/false field on the operator event.',
  },
  {
    domain: 'Applications',
    emoji: '📋',
    example: 'AI evaluates an application → outcome recorded directly',
    note: 'Add correct: true/false to each AI decision event in your log.',
  },
]

const INITIAL_FORM = {
  pilot_tag: '',
  pilot_domain: '',
  task_description: '',
  human_roles: [],
  human_actions: [],       // [{action_name, label}]
  ai_actions: [],          // [{action_name, label}]
  baseline_duration: '',
  baseline_duration_unit: 'seconds',
  max_reaction_time: '',
  max_reaction_time_unit: 'seconds',
  // Step 2
  correctness_description: '',
  correctness_strategy: 'add_field',   // 'add_field' | 'existing_field' | 'derived'
  correctness_field_name: 'correct',
  correctness_correct_value: 'true',
  correctness_incorrect_value: 'false',
  correctness_derive_condition: '',
}

// ── Shared helpers ─────────────────────────────────────────────────────────

function StepDots({ current }) {
  const labels = ['Environment', 'Correctness', 'Template', 'Activate']
  return (
    <div className="flex items-center gap-0 mb-8">
      {labels.map((label, i) => {
        const done   = i < current
        const active = i === current
        return (
          <div key={i} className="flex items-center">
            <div className="flex flex-col items-center gap-1">
              <div className={clsx(
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-colors',
                done   ? 'bg-indigo-600 text-white'
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
            {i < labels.length - 1 && (
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

// TagInput — list of plain strings
function TagInput({ value, onChange, placeholder }) {
  const [draft, setDraft] = useState('')

  function add() {
    const v = draft.trim()
    if (v && !value.includes(v)) onChange([...value, v])
    setDraft('')
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="flex-1 border border-gray-200 rounded-md px-3 py-1.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button
          type="button"
          onClick={add}
          disabled={!draft.trim()}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium
                     border border-indigo-200 text-indigo-600 hover:bg-indigo-50
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Plus size={12} /> Add
        </button>
      </div>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {value.map(t => (
            <span key={t} className="flex items-center gap-1 text-xs font-mono
                                     bg-indigo-50 text-indigo-700 border border-indigo-100
                                     rounded px-2 py-0.5">
              {t}
              <button
                type="button"
                onClick={() => onChange(value.filter(v => v !== t))}
                className="hover:text-red-500"
              >
                <X size={11} />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

// ActionDefInput — list of {action_name, label}
function ActionDefInput({ value, onChange, placeholder = 'action_name' }) {
  const [name, setName]   = useState('')
  const [label, setLabel] = useState('')

  function add() {
    const n = name.trim().replace(/\s+/g, '_').toLowerCase()
    if (n && !value.some(a => a.action_name === n)) {
      onChange([...value, { action_name: n, label: label.trim() || n }])
    }
    setName('')
    setLabel('')
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="w-44 border border-gray-200 rounded-md px-3 py-1.5 text-sm font-mono
                     focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <input
          value={label}
          onChange={e => setLabel(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder="Friendly label (optional)"
          className="flex-1 border border-gray-200 rounded-md px-3 py-1.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button
          type="button"
          onClick={add}
          disabled={!name.trim()}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium
                     border border-indigo-200 text-indigo-600 hover:bg-indigo-50
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Plus size={12} /> Add
        </button>
      </div>
      {value.length > 0 && (
        <div className="space-y-1">
          {value.map(a => (
            <div key={a.action_name}
                 className="flex items-center gap-2 text-xs bg-gray-50 rounded px-2 py-1">
              <span className="font-mono text-indigo-700">{a.action_name}</span>
              {a.label !== a.action_name && (
                <span className="text-gray-400">→ {a.label}</span>
              )}
              <button
                type="button"
                onClick={() => onChange(value.filter(v => v.action_name !== a.action_name))}
                className="ml-auto text-gray-300 hover:text-red-400"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// DurationInput — number + unit selector
function DurationInput({ value, unit, onValueChange, onUnitChange }) {
  return (
    <div className="flex gap-2">
      <input
        type="number"
        min="0"
        value={value}
        onChange={e => onValueChange(e.target.value)}
        placeholder="e.g. 30"
        className="w-28 border border-gray-200 rounded-md px-3 py-1.5 text-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-300"
      />
      <select
        value={unit}
        onChange={e => onUnitChange(e.target.value)}
        className="border border-gray-200 rounded-md px-3 py-1.5 text-sm bg-white
                   focus:outline-none focus:ring-2 focus:ring-indigo-300"
      >
        <option value="seconds">seconds</option>
        <option value="minutes">minutes</option>
      </select>
    </div>
  )
}

// ── Step 1 — Environment Definition ───────────────────────────────────────

function StepEnvDef({ form, onChange, onNext }) {
  const canProceed = form.pilot_tag.trim().length > 0
  const set = (key, val) => onChange({ ...form, [key]: val })

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h2 className="text-base font-semibold text-gray-900">Define your pilot environment</h2>
        <p className="text-sm text-gray-500 mt-1">
          This information generates a log template and configures which metrics will compute.
        </p>
      </div>

      <div className="space-y-5">
        {/* pilot_tag */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Pilot tag <span className="text-red-400">*</span>
          </label>
          <input
            value={form.pilot_tag}
            onChange={e => set('pilot_tag', e.target.value.replace(/\s+/g, '_').toLowerCase())}
            placeholder="e.g. radiology_assist"
            className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm font-mono
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
          <p className="text-xs text-gray-400 mt-1">Lowercase, no spaces. Used as the adapter identifier.</p>
        </div>

        {/* pilot_domain */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
          <select
            value={form.pilot_domain}
            onChange={e => set('pilot_domain', e.target.value)}
            className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          >
            <option value="">— Select domain —</option>
            {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        {/* task_description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Describe your task in one sentence
          </label>
          <input
            value={form.task_description}
            onChange={e => set('task_description', e.target.value)}
            placeholder="e.g. Radiologists review AI-generated diagnoses on CT scans"
            className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </div>

        {/* human_roles */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Who are the human actors?
          </label>
          <TagInput
            value={form.human_roles}
            onChange={v => set('human_roles', v)}
            placeholder="e.g. radiologist, operator, citizen"
          />
        </div>

        {/* human_actions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Human actions</label>
          <p className="text-xs text-gray-400 mb-1.5">
            Action names that appear in your logs for human events.
          </p>
          <ActionDefInput
            value={form.human_actions}
            onChange={v => set('human_actions', v)}
            placeholder="e.g. radiologist_confirms"
          />
        </div>

        {/* ai_actions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">AI actions</label>
          <p className="text-xs text-gray-400 mb-1.5">
            Action names that appear in your logs for AI events.
          </p>
          <ActionDefInput
            value={form.ai_actions}
            onChange={v => set('ai_actions', v)}
            placeholder="e.g. ai_diagnosis"
          />
        </div>

        {/* baseline_duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Baseline task duration without AI
          </label>
          <p className="text-xs text-gray-400 mb-1.5">Used to compute Effort Loss (EL). Leave blank to skip.</p>
          <DurationInput
            value={form.baseline_duration}
            unit={form.baseline_duration_unit}
            onValueChange={v => set('baseline_duration', v)}
            onUnitChange={v => set('baseline_duration_unit', v)}
          />
        </div>

        {/* max_reaction_time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max acceptable human reaction time
          </label>
          <p className="text-xs text-gray-400 mb-1.5">Used as the HCL threshold. Leave blank for the domain default.</p>
          <DurationInput
            value={form.max_reaction_time}
            unit={form.max_reaction_time_unit}
            onValueChange={v => set('max_reaction_time', v)}
            onUnitChange={v => set('max_reaction_time_unit', v)}
          />
        </div>
      </div>

      <button
        disabled={!canProceed}
        onClick={onNext}
        className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                   bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Next <ChevronRight size={14} />
      </button>
    </div>
  )
}

// ── Step 2 — Define Correctness ────────────────────────────────────────────

function StepCorrectness({ form, onChange, onNext, onBack }) {
  const set = (key, val) => onChange({ ...form, [key]: val })

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h2 className="text-base font-semibold text-gray-900">Define correctness</h2>
        <p className="text-sm text-gray-500 mt-1">
          When is the AI correct in your domain? This determines whether Trust (Tr) can be computed.
        </p>
      </div>

      {/* Domain example cards */}
      <div className="grid grid-cols-3 gap-3">
        {DOMAIN_EXAMPLES.map(ex => (
          <div key={ex.domain} className="rounded-lg border border-gray-100 bg-gray-50 p-3 space-y-1.5">
            <p className="text-xs font-semibold text-gray-700">{ex.emoji} {ex.domain}</p>
            <p className="text-xs text-gray-500 italic">{ex.example}</p>
            <p className="text-xs text-gray-400">{ex.note}</p>
          </div>
        ))}
      </div>

      {/* Free-text description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Describe when the AI is correct in your domain
        </label>
        <textarea
          rows={2}
          value={form.correctness_description}
          onChange={e => set('correctness_description', e.target.value)}
          placeholder="e.g. The AI is correct when the operator validates the recommendation without modification"
          className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none"
        />
      </div>

      {/* Strategy radio group */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Which field in your log captures this?
        </label>
        <div className="space-y-4">

          {/* add_field */}
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="radio"
              name="cstrat"
              value="add_field"
              checked={form.correctness_strategy === 'add_field'}
              onChange={() => set('correctness_strategy', 'add_field')}
              className="mt-0.5 text-indigo-600"
            />
            <div>
              <p className="text-sm text-gray-800">
                I will add a{' '}
                <code className="text-xs font-mono bg-gray-100 rounded px-1 py-0.5">correct: true/false</code>
                {' '}field to each AI event
              </p>
              <p className="text-xs text-gray-400">Simplest approach — recommended for new pilots</p>
            </div>
          </label>

          {/* existing_field */}
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="radio"
              name="cstrat"
              value="existing_field"
              checked={form.correctness_strategy === 'existing_field'}
              onChange={() => set('correctness_strategy', 'existing_field')}
              className="mt-0.5 text-indigo-600"
            />
            <div className="flex-1 space-y-2">
              <p className="text-sm text-gray-800 flex flex-wrap items-center gap-1">
                My log has
                <input
                  value={form.correctness_field_name}
                  onChange={e => set('correctness_field_name', e.target.value)}
                  onClick={() => set('correctness_strategy', 'existing_field')}
                  placeholder="field name"
                  className="w-28 border-b border-gray-300 px-1 py-0 text-sm font-mono
                             focus:outline-none focus:border-indigo-400 bg-transparent"
                />
                where
                <input
                  value={form.correctness_correct_value}
                  onChange={e => set('correctness_correct_value', e.target.value)}
                  onClick={() => set('correctness_strategy', 'existing_field')}
                  placeholder="value"
                  className="w-20 border-b border-gray-300 px-1 py-0 text-sm font-mono
                             focus:outline-none focus:border-indigo-400 bg-transparent"
                />
                means correct
              </p>
              {form.correctness_strategy === 'existing_field' && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Incorrect value:</span>
                  <input
                    value={form.correctness_incorrect_value}
                    onChange={e => set('correctness_incorrect_value', e.target.value)}
                    placeholder="false"
                    className="w-20 border border-gray-200 rounded px-2 py-0.5 text-xs font-mono
                               focus:outline-none focus:ring-1 focus:ring-indigo-300"
                  />
                </div>
              )}
            </div>
          </label>

          {/* derived */}
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="radio"
              name="cstrat"
              value="derived"
              checked={form.correctness_strategy === 'derived'}
              onChange={() => set('correctness_strategy', 'derived')}
              className="mt-0.5 text-indigo-600"
            />
            <div className="flex-1">
              <p className="text-sm text-gray-800">Correctness can be derived: AI is correct when</p>
              <input
                value={form.correctness_derive_condition}
                onChange={e => set('correctness_derive_condition', e.target.value)}
                onClick={() => set('correctness_strategy', 'derived')}
                placeholder="e.g. operator_confirms happens without a subsequent override event"
                className="mt-1 w-full border border-gray-200 rounded-md px-3 py-1.5 text-sm
                           focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
              <p className="text-xs text-gray-400 mt-1">
                Note: derived correctness requires post-processing. Add a{' '}
                <code className="font-mono">correct</code> field to your logs for Tr to compute automatically.
              </p>
            </div>
          </label>

        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="flex items-center gap-1 px-4 py-2 rounded-md text-sm font-medium
                     border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
        >
          <ChevronLeft size={14} /> Back
        </button>
        <button
          onClick={onNext}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                     bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
        >
          Next <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

// ── Step 3 — Generated Template ────────────────────────────────────────────

function generateLogTemplate(form) {
  const aiAction    = form.ai_actions[0]?.action_name    || 'ai_evaluated'
  const humanAction = form.human_actions[0]?.action_name || 'human_reviewed'

  const aiEvent = {
    interaction_id: 'evt_001',
    timestamp:      '2024-01-01T10:00:00Z',
    event_type:     aiAction,
    actor_type:     'ai',
    latency_ms:     120,
  }
  if (form.correctness_strategy === 'add_field') {
    aiEvent.correct = true
  } else if (form.correctness_strategy === 'existing_field') {
    aiEvent[form.correctness_field_name || 'correct'] = form.correctness_correct_value || 'true'
  }

  const humanEvent = {
    interaction_id: 'evt_002',
    timestamp:      '2024-01-01T10:00:05Z',
    event_type:     humanAction,
    actor_type:     'human',
    duration_s:     5.2,
  }

  const session = { session_id: 'session_001', decisions: [aiEvent, humanEvent] }
  if (form.baseline_duration) {
    const v = parseFloat(form.baseline_duration)
    if (!isNaN(v)) {
      session.baseline_s = form.baseline_duration_unit === 'minutes' ? v * 60 : v
    }
  }
  return [session]
}

function generateAdapterConfig(form) {
  const cfg = {
    pilot_tag:          form.pilot_tag,
    ai_action_names:    form.ai_actions.map(a => a.action_name),
    human_action_names: form.human_actions.map(a => a.action_name),
  }
  if (form.correctness_strategy === 'existing_field') {
    cfg.correct_field   = form.correctness_field_name   || 'correct'
    cfg.correct_value   = form.correctness_correct_value  || 'true'
    cfg.incorrect_value = form.correctness_incorrect_value || 'false'
  }
  if (form.baseline_duration) {
    const v = parseFloat(form.baseline_duration)
    if (!isNaN(v)) {
      cfg.baseline_s = form.baseline_duration_unit === 'minutes' ? v * 60 : v
    }
  }
  return cfg
}

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function StepTemplate({ form, onNext, onBack }) {
  const template   = useMemo(() => generateLogTemplate(form),   [form])
  const adapterCfg = useMemo(() => generateAdapterConfig(form), [form])

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-base font-semibold text-gray-900">Generated log template</h2>
        <p className="text-sm text-gray-500 mt-1">
          Use this JSON structure for your log files. Download both files before proceeding.
        </p>
      </div>

      {/* Log template */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-gray-700">Log template</p>
          <button
            onClick={() => downloadJson(template, `${form.pilot_tag}_log_template.json`)}
            className="flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            <Download size={12} /> Download template
          </button>
        </div>
        <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 text-xs overflow-x-auto
                        leading-relaxed max-h-64 overflow-y-auto">
          {JSON.stringify(template, null, 2)}
        </pre>
      </div>

      {/* Adapter config */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-gray-700">Adapter config</p>
          <button
            onClick={() => downloadJson(adapterCfg, `${form.pilot_tag}_adapter.json`)}
            className="flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            <Download size={12} /> Download adapter config
          </button>
        </div>
        <pre className="bg-gray-50 border border-gray-100 rounded-lg p-4 text-xs overflow-x-auto
                        leading-relaxed text-gray-700 max-h-48 overflow-y-auto">
          {JSON.stringify(adapterCfg, null, 2)}
        </pre>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="flex items-center gap-1 px-4 py-2 rounded-md text-sm font-medium
                     border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
        >
          <ChevronLeft size={14} /> Back
        </button>
        <button
          onClick={onNext}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                     bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
        >
          Next <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

// ── Step 4 — Confirm & Activate ────────────────────────────────────────────

function getMetricsSummary(form) {
  const hasHuman   = form.human_actions.length > 0
  const hasAi      = form.ai_actions.length > 0
  const hasCorrect = form.correctness_strategy !== 'derived'
  const hasBaseline = !!form.baseline_duration && !isNaN(parseFloat(form.baseline_duration))

  return [
    {
      metric: 'F',
      name:   'Interaction Frequency',
      ok:     hasHuman || hasAi,
      note:   hasHuman || hasAi ? 'always computes' : 'define at least one action first',
    },
    {
      metric: 'D',
      name:   'Mean Duration',
      ok:     hasHuman,
      note:   hasHuman ? 'computes if timing fields present' : 'define human actions first',
    },
    {
      metric: 'Tr',
      name:   'Trust',
      ok:     hasCorrect,
      note:   hasCorrect ? 'computes if correct field defined' : 'use add-field or existing-field in Step 2',
    },
    {
      metric: 'HCL',
      name:   'Human Cognitive Load',
      ok:     hasHuman,
      note:   hasHuman ? 'computes if human timing fields present' : 'define human actions first',
    },
    {
      metric: 'EL',
      name:   'Effort Loss',
      ok:     hasBaseline,
      note:   hasBaseline ? 'computes with your baseline' : 'no baseline defined in Step 1',
    },
    {
      metric: 'A',
      name:   'Agreement / Alignment',
      ok:     false,
      note:   'needs multiple sessions with labeled events',
    },
  ]
}

function StepActivate({ form, onBack, onActivate, isPending, error }) {
  const metrics    = useMemo(() => getMetricsSummary(form),    [form])
  const adapterCfg = useMemo(() => generateAdapterConfig(form), [form])

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h2 className="text-base font-semibold text-gray-900">Confirm and activate</h2>
        <p className="text-sm text-gray-500 mt-1">
          Review which metrics will compute, then activate your pilot.
        </p>
      </div>

      {/* Metrics summary */}
      <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 space-y-3">
        {metrics.map(m => (
          <div key={m.metric} className="flex items-start gap-3">
            {m.ok
              ? <CheckCircle2 size={15} className="text-green-500 mt-0.5 flex-shrink-0" />
              : <XCircle      size={15} className="text-gray-300 mt-0.5 flex-shrink-0" />}
            <div>
              <span className="text-sm font-mono font-semibold text-gray-800">{m.metric}</span>
              <span className="text-sm text-gray-600 ml-1.5">({m.name})</span>
              <span className="ml-2 text-xs text-gray-400">— {m.note}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Config summary */}
      <div className="text-sm text-gray-600 space-y-1">
        <p>
          <span className="font-medium">Pilot tag: </span>
          <code className="font-mono text-xs bg-gray-100 rounded px-1">{form.pilot_tag}</code>
        </p>
        {form.pilot_domain && (
          <p><span className="font-medium">Domain: </span>{form.pilot_domain}</p>
        )}
        {form.task_description && (
          <p><span className="font-medium">Task: </span>{form.task_description}</p>
        )}
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          disabled={isPending}
          className="flex items-center gap-1 px-4 py-2 rounded-md text-sm font-medium
                     border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors
                     disabled:opacity-40"
        >
          <ChevronLeft size={14} /> Back
        </button>
        <button
          onClick={() => onActivate(adapterCfg)}
          disabled={isPending}
          className="flex items-center gap-1.5 px-5 py-2 rounded-md text-sm font-medium
                     bg-green-600 text-white hover:bg-green-700 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isPending
            ? 'Activating…'
            : <><Rocket size={14} /> Activate pilot</>
          }
        </button>
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────

export default function PilotOnboardingPage() {
  const navigate = useNavigate()
  const [step,          setStep]          = useState(0)
  const [form,          setForm]          = useState(INITIAL_FORM)
  const [activateError, setActivateError] = useState(null)

  const { mutate, isPending } = useMutation({
    mutationFn: (payload) => api.pilot.onboard(payload),
    onSuccess: () => navigate('/ingest'),
    onError:   (err) => setActivateError(err.message),
  })

  function handleActivate(adapterCfg) {
    setActivateError(null)
    const toSeconds = (val, unit) => {
      const v = parseFloat(val)
      return isNaN(v) ? null : (unit === 'minutes' ? v * 60 : v)
    }
    mutate({
      pilot_tag:        form.pilot_tag,
      pilot_domain:     form.pilot_domain,
      task_description: form.task_description,
      human_roles:      form.human_roles,
      human_actions:    form.human_actions,
      ai_actions:       form.ai_actions,
      baseline_duration_s:  toSeconds(form.baseline_duration,    form.baseline_duration_unit),
      max_reaction_time_s:  toSeconds(form.max_reaction_time,    form.max_reaction_time_unit),
      correctness_rule: {
        strategy:          form.correctness_strategy,
        field_name:        form.correctness_field_name,
        correct_value:     form.correctness_correct_value,
        incorrect_value:   form.correctness_incorrect_value,
        derive_condition:  form.correctness_derive_condition,
        description:       form.correctness_description,
      },
      adapter_config: adapterCfg,
    })
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-900">New Pilot Setup</h1>
        <p className="text-sm text-gray-500 mt-1">
          Configure a new Human-AI collaboration pilot from scratch.
        </p>
      </div>

      <StepDots current={step} />

      {step === 0 && (
        <StepEnvDef form={form} onChange={setForm} onNext={() => setStep(1)} />
      )}
      {step === 1 && (
        <StepCorrectness
          form={form} onChange={setForm}
          onNext={() => setStep(2)} onBack={() => setStep(0)}
        />
      )}
      {step === 2 && (
        <StepTemplate
          form={form}
          onNext={() => setStep(3)} onBack={() => setStep(1)}
        />
      )}
      {step === 3 && (
        <StepActivate
          form={form}
          onBack={() => setStep(2)}
          onActivate={handleActivate}
          isPending={isPending}
          error={activateError}
        />
      )}
    </div>
  )
}
