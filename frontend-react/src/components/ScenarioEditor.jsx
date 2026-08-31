import { useState } from 'react'
import { Plus, Trash2, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

function makeKey() {
  return crypto.randomUUID?.() || Math.random().toString(36).slice(2)
}

function newAgent() {
  return { _key: makeKey(), name: '' }
}

function newStep() {
  return { _key: makeKey(), actor: '', action: '', actorType: 'ai', timing: '', correct: 'unset' }
}

const INPUT = `w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm text-gray-700
  focus:outline-none focus:ring-2 focus:ring-indigo-300`

function AgentRow({ agent, onChange, onDelete }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        value={agent.name}
        onChange={(e) => onChange({ ...agent, name: e.target.value })}
        placeholder="e.g. AI_Model, Reviewer"
        className={INPUT}
      />
      <button onClick={onDelete} className="p-1.5 text-gray-400 hover:text-red-600 rounded flex-shrink-0" title="Remove agent">
        <Trash2 size={13} />
      </button>
    </div>
  )
}

function StepRow({ step, index, agentNames, onChange, onDelete, error }) {
  function update(patch) {
    onChange({ ...step, ...patch })
  }
  return (
    <div className={clsx('rounded-md border p-3 space-y-2', error ? 'border-red-300' : 'border-gray-200')}>
      {error && <p className="text-xs text-red-600">{error}</p>}
      <div className="grid grid-cols-12 gap-2 items-center">
        <span className="col-span-1 text-xs text-gray-400 font-mono">#{index + 1}</span>
        <select
          value={step.actor}
          onChange={(e) => update({ actor: e.target.value })}
          className={clsx(INPUT, 'col-span-3')}
        >
          <option value="">Actor…</option>
          {agentNames.map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
        <input
          type="text"
          value={step.action}
          onChange={(e) => update({ action: e.target.value })}
          placeholder="Action, e.g. propose_label"
          className={clsx(INPUT, 'col-span-4')}
        />
        <select
          value={step.actorType}
          onChange={(e) => update({ actorType: e.target.value })}
          className={clsx(INPUT, 'col-span-2')}
        >
          <option value="ai">AI</option>
          <option value="human">Human</option>
        </select>
        <input
          type="number"
          min={0}
          step="any"
          value={step.timing}
          onChange={(e) => update({ timing: e.target.value })}
          placeholder={step.actorType === 'human' ? 'seconds' : 'ms'}
          title={step.actorType === 'human' ? 'Duration in seconds' : 'Latency in milliseconds'}
          className={clsx(INPUT, 'col-span-1')}
        />
        <button onClick={onDelete} className="col-span-1 p-1.5 text-gray-400 hover:text-red-600 rounded justify-self-end" title="Remove step">
          <Trash2 size={13} />
        </button>
      </div>
      <div className="flex items-center gap-3 pl-1">
        <span className="text-xs text-gray-500">Outcome:</span>
        {['unset', 'true', 'false'].map((v) => (
          <label key={v} className="flex items-center gap-1 text-xs text-gray-600">
            <input
              type="radio"
              name={`correct-${step._key}`}
              checked={step.correct === v}
              onChange={() => update({ correct: v })}
            />
            {v === 'unset' ? 'n/a' : v === 'true' ? 'correct' : 'incorrect'}
          </label>
        ))}
      </div>
    </div>
  )
}

function validate(form) {
  if (!form.taskName.trim()) return 'Scenario name is required.'
  const names = form.agents.map((a) => a.name.trim()).filter(Boolean)
  if (names.length < 1) return 'Add at least one agent.'
  if (new Set(names).size !== names.length) return 'Agent names must be unique.'
  if (form.steps.length < 1) return 'Add at least one script step.'

  const stepErrors = {}
  for (const s of form.steps) {
    if (!s.actor) stepErrors[s._key] = 'Pick an actor for this step.'
    else if (!names.includes(s.actor)) stepErrors[s._key] = `"${s.actor}" is not a defined agent.`
    else if (!s.action.trim()) stepErrors[s._key] = 'This step needs an action name.'
    else if (s.timing === '' || Number(s.timing) < 0) stepErrors[s._key] = 'This step needs a timing value.'
  }
  return { stepErrors }
}

export default function ScenarioEditor({ onCreated }) {
  const [form, setForm] = useState({
    taskName: '', taskDescription: '', rtMax: 5, baselineS: '',
    agents: [newAgent(), newAgent()],
    steps: [newStep()],
  })
  const [saving, setSaving] = useState(false)
  const [saveResult, setSaveResult] = useState(null)

  function addAgent() {
    setForm((f) => ({ ...f, agents: [...f.agents, newAgent()] }))
  }
  function updateAgent(key, updated) {
    setForm((f) => ({ ...f, agents: f.agents.map((a) => (a._key === key ? updated : a)) }))
  }
  function deleteAgent(key) {
    setForm((f) => ({ ...f, agents: f.agents.filter((a) => a._key !== key) }))
  }

  function addStep() {
    setForm((f) => ({ ...f, steps: [...f.steps, newStep()] }))
  }
  function updateStep(key, updated) {
    setForm((f) => ({ ...f, steps: f.steps.map((s) => (s._key === key ? updated : s)) }))
  }
  function deleteStep(key) {
    setForm((f) => ({ ...f, steps: f.steps.filter((s) => s._key !== key) }))
  }

  const validation = validate(form)
  const globalError = typeof validation === 'string' ? validation : null
  const stepErrors = typeof validation === 'string' ? {} : validation.stepErrors
  const canSave = !globalError && Object.keys(stepErrors).length === 0

  async function handleSave() {
    if (!canSave) return
    setSaving(true)
    setSaveResult(null)
    try {
      const actions = form.steps.map((s) => {
        const action = { actor: s.actor, name: s.action.trim() }
        if (s.actorType === 'human') action.duration_s = Number(s.timing)
        else action.latency_ms = Number(s.timing)
        if (s.correct !== 'unset') action.correct = s.correct === 'true'
        return action
      })

      const payload = {
        task_name: form.taskName.trim(),
        task_description: form.taskDescription.trim() || null,
        task_parameters: {
          environment: 'scripted',
          rt_max: Number(form.rtMax) || 5.0,
          ...(form.baselineS !== '' && { baseline_s: Number(form.baselineS) }),
          env_params: { script: { tasks: [{ actions }] } },
        },
        agent_definitions: form.agents
          .filter((a) => a.name.trim())
          .map((a) => ({ name: a.name.trim() })),
        profile_definitions: [],
      }

      const out = await api.envBuilder.generateConfig(payload)
      setSaveResult({ type: 'success', path: out.path })
      onCreated?.(out.path)
    } catch (e) {
      setSaveResult({ type: 'error', text: e.message || 'Failed to save scenario.' })
    } finally {
      setSaving(false)
    }
  }

  const agentNames = form.agents.map((a) => a.name.trim()).filter(Boolean)

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-xs text-sky-800">
        Define the agents involved and a script of steps they take, in order. Each step is either
        an AI action (latency in milliseconds) or a human action (duration in seconds) — that
        distinction is what drives the Human-AI metrics.
      </div>

      <div className="grid grid-cols-2 gap-3">
        <label className="block col-span-2">
          <span className="mb-1 block text-xs font-medium text-gray-600">Scenario name</span>
          <input
            type="text"
            value={form.taskName}
            onChange={(e) => setForm((f) => ({ ...f, taskName: e.target.value }))}
            placeholder="e.g. Ticket Triage Review"
            className={INPUT}
          />
        </label>
        <label className="block col-span-2">
          <span className="mb-1 block text-xs font-medium text-gray-600">Description (optional)</span>
          <input
            type="text"
            value={form.taskDescription}
            onChange={(e) => setForm((f) => ({ ...f, taskDescription: e.target.value }))}
            className={INPUT}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-gray-600">Max acceptable human response time (s)</span>
          <input
            type="number" min={0} step="any"
            value={form.rtMax}
            onChange={(e) => setForm((f) => ({ ...f, rtMax: e.target.value }))}
            className={INPUT}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-gray-600">Baseline time without AI (s, optional)</span>
          <input
            type="number" min={0} step="any"
            value={form.baselineS}
            onChange={(e) => setForm((f) => ({ ...f, baselineS: e.target.value }))}
            placeholder="auto-derive if blank"
            className={INPUT}
          />
        </label>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Agents</span>
          <button onClick={addAgent} className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800">
            <Plus size={13} /> Add agent
          </button>
        </div>
        <div className="space-y-2">
          {form.agents.map((a) => (
            <AgentRow key={a._key} agent={a} onChange={(u) => updateAgent(a._key, u)} onDelete={() => deleteAgent(a._key)} />
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Script steps (in order)</span>
          <button onClick={addStep} className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800">
            <Plus size={13} /> Add step
          </button>
        </div>
        <div className="space-y-2">
          {form.steps.map((s, i) => (
            <StepRow
              key={s._key} step={s} index={i} agentNames={agentNames}
              onChange={(u) => updateStep(s._key, u)}
              onDelete={() => deleteStep(s._key)}
              error={stepErrors[s._key]}
            />
          ))}
        </div>
      </div>

      {globalError && <p className="text-xs text-red-600">{globalError}</p>}

      <button
        onClick={handleSave}
        disabled={saving || !canSave}
        className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {saving && <Loader2 size={14} className="animate-spin" />}
        Save scenario
      </button>

      {saveResult?.type === 'error' && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
          {saveResult.text}
        </div>
      )}
    </div>
  )
}
