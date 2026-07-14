import { useState } from 'react'
import { Plus, Copy, Trash2, ChevronDown, Download, Upload, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

const TYPES = [
  { value: 'likert', label: 'Likert (1–5)' },
  { value: 'single', label: 'Single choice' },
  { value: 'multi', label: 'Multi choice' },
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'boolean', label: 'Boolean' },
]

function makeKey() {
  return crypto.randomUUID?.() || Math.random().toString(36).slice(2)
}

function slug(s) {
  return String(s || '').toLowerCase().trim().replace(/\s+/g, '_').replace(/[^\w-]/g, '')
}

function newQuestion() {
  return {
    _key: makeKey(),
    id: '',
    label: '',
    type: 'likert',
    required: false,
    group: '',
    scale: { min: 1, max: 5, min_label: 'Strongly disagree', max_label: 'Strongly agree' },
    options: [],
  }
}

function OptionsEditor({ options, onChange }) {
  const [draft, setDraft] = useState('')

  function add() {
    const v = draft.trim()
    if (!v || options.includes(v)) return
    onChange([...options, v])
    setDraft('')
  }

  return (
    <div>
      <div className="flex flex-wrap gap-1.5 mb-1.5">
        {options.map((opt) => (
          <span key={opt} className="inline-flex items-center gap-1 rounded-full bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5">
            {opt}
            <button onClick={() => onChange(options.filter((o) => o !== opt))} className="hover:text-indigo-900">×</button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
        placeholder="Type an option, press Enter"
        className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-xs text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
      />
    </div>
  )
}

function QuestionCard({ q, index, expanded, onToggle, onChange, onDuplicate, onDelete, error }) {
  function update(patch) {
    onChange({ ...q, ...patch })
  }

  return (
    <div className={clsx('rounded-lg border bg-white', error ? 'border-red-300' : 'border-gray-200')}>
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-2 px-3 py-2.5 text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs text-gray-400 flex-shrink-0">#{index + 1}</span>
          <span className="text-sm text-gray-700 truncate">{q.label || <span className="text-gray-400">Untitled question</span>}</span>
          <span className="flex-shrink-0 rounded bg-gray-100 text-gray-500 text-[10px] px-1.5 py-0.5 uppercase tracking-wide">
            {q.type}
          </span>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <span
            role="button"
            onClick={(e) => { e.stopPropagation(); onDuplicate() }}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title="Duplicate"
          >
            <Copy size={13} />
          </span>
          <span
            role="button"
            onClick={(e) => { e.stopPropagation(); onDelete() }}
            className="p-1 text-gray-400 hover:text-red-600 rounded"
            title="Delete"
          >
            <Trash2 size={13} />
          </span>
          <ChevronDown size={14} className={clsx('text-gray-400 transition-transform', expanded && 'rotate-180')} />
        </div>
      </button>

      {expanded && (
        <div className="space-y-3 px-3 pb-3 border-t border-gray-100 pt-3">
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="grid grid-cols-2 gap-3">
            <label className="block col-span-2">
              <span className="mb-1 block text-xs font-medium text-gray-600">Label</span>
              <input
                type="text"
                value={q.label}
                onChange={(e) => update({ label: e.target.value })}
                onBlur={() => { if (!q.id && q.label) update({ id: slug(q.label) }) }}
                className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-gray-600">ID (stable key)</span>
              <input
                type="text"
                value={q.id}
                onChange={(e) => update({ id: e.target.value })}
                className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm font-mono text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-gray-600">Type</span>
              <select
                value={q.type}
                onChange={(e) => update({ type: e.target.value })}
                className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700"
              >
                {TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-gray-600">Group (section)</span>
              <input
                type="text"
                value={q.group}
                onChange={(e) => update({ group: e.target.value })}
                className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </label>
            <label className="flex items-center gap-2 text-xs text-gray-600">
              <input type="checkbox" checked={q.required} onChange={(e) => update({ required: e.target.checked })} />
              Required
            </label>
          </div>

          {q.type === 'likert' && (
            <div className="grid grid-cols-4 gap-3">
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-gray-600">Min</span>
                <input type="number" value={q.scale.min} onChange={(e) => update({ scale: { ...q.scale, min: Number(e.target.value) } })}
                  className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700" />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-gray-600">Max</span>
                <input type="number" value={q.scale.max} onChange={(e) => update({ scale: { ...q.scale, max: Number(e.target.value) } })}
                  className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700" />
              </label>
              <label className="block col-span-2">
                <span className="mb-1 block text-xs font-medium text-gray-600">Min label</span>
                <input type="text" value={q.scale.min_label} onChange={(e) => update({ scale: { ...q.scale, min_label: e.target.value } })}
                  className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700" />
              </label>
              <label className="block col-span-2">
                <span className="mb-1 block text-xs font-medium text-gray-600">Max label</span>
                <input type="text" value={q.scale.max_label} onChange={(e) => update({ scale: { ...q.scale, max_label: e.target.value } })}
                  className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700" />
              </label>
            </div>
          )}

          {(q.type === 'single' || q.type === 'multi') && (
            <div>
              <span className="mb-1 block text-xs font-medium text-gray-600">Options</span>
              <OptionsEditor options={q.options} onChange={(options) => update({ options })} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function validate(form) {
  const errors = {}
  let globalError = ''
  if (!form.name.trim()) globalError = 'Name is required.'
  if (!form.questions.length) globalError = globalError || 'Add at least one question.'

  const ids = new Set()
  for (const q of form.questions) {
    if (!q.id) { errors[q._key] = 'This question needs an ID.'; continue }
    if (ids.has(q.id)) { errors[q._key] = `Duplicate ID "${q.id}".`; continue }
    ids.add(q.id)
    if (q.type === 'likert' && !(Number.isFinite(q.scale.min) && Number.isFinite(q.scale.max) && q.scale.min < q.scale.max)) {
      errors[q._key] = 'Invalid Likert scale (min must be less than max).'
    }
    if ((q.type === 'single' || q.type === 'multi') && !q.options.length) {
      errors[q._key] = 'Add at least one option.'
    }
  }
  return { globalError, errors }
}

export default function QuestionSetEditor({ pilotTag, onCreated }) {
  const [form, setForm] = useState({
    name: '', pilotTag: pilotTag || '', version: 1, active: true, questions: [],
  })
  const [expanded, setExpanded] = useState(new Set())
  const [saving, setSaving] = useState(false)
  const [saveResult, setSaveResult] = useState(null) // { type: 'success'|'error', text }

  function addQuestion() {
    const q = newQuestion()
    setForm((f) => ({ ...f, questions: [...f.questions, q] }))
    setExpanded((s) => new Set(s).add(q._key))
  }

  function updateQuestion(key, updated) {
    setForm((f) => ({ ...f, questions: f.questions.map((q) => (q._key === key ? updated : q)) }))
  }

  function duplicateQuestion(index) {
    const q = form.questions[index]
    const copy = { ...JSON.parse(JSON.stringify(q)), _key: makeKey(), id: q.id ? `${q.id}_copy` : '' }
    setForm((f) => {
      const questions = [...f.questions]
      questions.splice(index + 1, 0, copy)
      return { ...f, questions }
    })
    setExpanded((s) => new Set(s).add(copy._key))
  }

  function deleteQuestion(key) {
    setForm((f) => ({ ...f, questions: f.questions.filter((q) => q._key !== key) }))
  }

  function toggle(key) {
    setExpanded((s) => {
      const next = new Set(s)
      if (next.has(key)) next.delete(key); else next.add(key)
      return next
    })
  }

  const { globalError, errors } = validate(form)

  async function handleSave() {
    if (globalError || Object.keys(errors).length) return
    setSaving(true)
    setSaveResult(null)
    try {
      const payload = {
        name: form.name,
        pilot_tag: form.pilotTag || null,
        version: form.version || 1,
        active: form.active,
        questions: form.questions.map((q) => ({
          id: q.id, label: q.label, type: q.type, required: q.required,
          group: q.group || null,
          scale: q.type === 'likert' ? q.scale : null,
          options: (q.type === 'single' || q.type === 'multi') && q.options.length ? q.options : null,
        })),
      }
      const out = await api.survey.schemas.create(payload)
      setSaveResult({ type: 'success', schemaId: out.schema_id })
      onCreated?.(out)
    } catch (e) {
      setSaveResult({ type: 'error', text: e.message || 'Failed to save.' })
    } finally {
      setSaving(false)
    }
  }

  function handleExport() {
    const blob = new Blob([JSON.stringify(form, null, 2)], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'question_set.json'
    link.click()
    URL.revokeObjectURL(link.href)
  }

  function handleImport() {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'application/json'
    input.onchange = (e) => {
      const file = e.target.files?.[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const obj = JSON.parse(reader.result)
          setForm({
            name: obj.name || '',
            pilotTag: obj.pilot_tag || form.pilotTag,
            version: obj.version || 1,
            active: obj.active ?? true,
            questions: (obj.questions || []).map((q) => ({
              _key: makeKey(),
              scale: { min: 1, max: 5, min_label: 'Strongly disagree', max_label: 'Strongly agree' },
              options: [],
              group: '',
              required: false,
              ...q,
            })),
          })
        } catch {
          setSaveResult({ type: 'error', text: 'Invalid JSON file.' })
        }
      }
      reader.readAsText(file)
    }
    input.click()
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-xs text-sky-800">
        Create a pilot-specific question set. Saving returns a <code className="rounded bg-white px-1">schema_id</code> that
        gets auto-attached to the survey link.
      </div>

      <div className="grid grid-cols-2 gap-3">
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-gray-600">Name</span>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="SmartEnergy v1"
            className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-gray-600">
            Pilot tag {pilotTag && <span className="text-gray-400">(from configuration)</span>}
          </span>
          <input
            type="text"
            value={form.pilotTag}
            readOnly={!!pilotTag}
            onChange={(e) => setForm((f) => ({ ...f, pilotTag: e.target.value }))}
            className={clsx(
              'w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700',
              pilotTag && 'bg-gray-50',
            )}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-gray-600">Version</span>
          <input
            type="number"
            min={1}
            value={form.version}
            onChange={(e) => setForm((f) => ({ ...f, version: Number(e.target.value) }))}
            className="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700"
          />
        </label>
        <label className="flex items-center gap-2 text-xs text-gray-600 mt-5">
          <input type="checkbox" checked={form.active} onChange={(e) => setForm((f) => ({ ...f, active: e.target.checked }))} />
          Active
        </label>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Questions</span>
        <button
          onClick={addQuestion}
          className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800"
        >
          <Plus size={13} /> Add question
        </button>
      </div>

      {form.questions.length === 0 && (
        <p className="text-xs text-gray-400 text-center py-4">No questions yet — add one above.</p>
      )}

      <div className="space-y-2">
        {form.questions.map((q, i) => (
          <QuestionCard
            key={q._key}
            q={q}
            index={i}
            expanded={expanded.has(q._key)}
            onToggle={() => toggle(q._key)}
            onChange={(updated) => updateQuestion(q._key, updated)}
            onDuplicate={() => duplicateQuestion(i)}
            onDelete={() => deleteQuestion(q._key)}
            error={errors[q._key]}
          />
        ))}
      </div>

      {globalError && <p className="text-xs text-red-600">{globalError}</p>}

      <div className="flex items-center gap-3 pt-1">
        <button
          onClick={handleSave}
          disabled={saving || !!globalError || Object.keys(errors).length > 0}
          className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving && <Loader2 size={14} className="animate-spin" />}
          Save question set
        </button>
        <button onClick={handleExport} className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
          <Download size={12} /> Export JSON
        </button>
        <button onClick={handleImport} className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
          <Upload size={12} /> Import JSON
        </button>
      </div>

      {saveResult?.type === 'success' && (
        <div className="rounded-md bg-green-50 border border-green-200 px-3 py-2 text-xs text-green-700">
          Saved. schema_id: <code className="font-mono">{saveResult.schemaId}</code>
        </div>
      )}
      {saveResult?.type === 'error' && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
          {saveResult.text}
        </div>
      )}
    </div>
  )
}
