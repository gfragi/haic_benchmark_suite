import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, AlertCircle, Loader2, Plus, X } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

const STATUS = {
  completed: 'bg-green-100 text-green-800',
  running:   'bg-blue-100 text-blue-800',
  failed:    'bg-red-100 text-red-800',
  pending:   'bg-gray-100 text-gray-500',
}

function StatusBadge({ status }) {
  const s = status?.toLowerCase() ?? 'pending'
  return (
    <span className={clsx(
      'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize',
      STATUS[s] ?? STATUS.pending,
    )}>
      {s}
    </span>
  )
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-GB', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

// ── New Config Modal ─────────────────────────────────────────

const EMPTY_FORM = {
  application_name: '',
  ai_model_name: '',
  ai_model_type: '',
  description: '',
  config_type: '',
  metrics: [],
}

const AI_MODEL_TYPES = [
  'Classification', 'Regression', 'Clustering',
  'XAI', 'Swarm Learning', 'Active Learning', 'Other',
]
const CONFIG_TYPES = ['specific', 'generic']
const METRIC_GROUPS = [
  'Effectiveness', 'Efficiency', 'Adaptability and Learning',
  'Collaboration and Interaction', 'Trust and Safety', 'Robustness and Generalization',
]

function Field({ label, required, children }) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 mb-1">
        {label}{required && <span className="text-red-400 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  )
}

const INPUT = `w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700
  focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white`

function NewConfigModal({ onClose, onCreated }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  function set(key, val) {
    setForm(f => ({ ...f, [key]: val }))
  }

  const canSave = form.application_name.trim() && form.ai_model_name.trim()
    && form.ai_model_type && form.config_type && form.metrics.length > 0

  function toggleMetric(m) {
    setForm(f => ({
      ...f,
      metrics: f.metrics.includes(m) ? f.metrics.filter(x => x !== m) : [...f.metrics, m],
    }))
  }

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      const payload = {
        application_name: form.application_name.trim(),
        ai_model_name: form.ai_model_name.trim(),
        ai_model_type: form.ai_model_type,
        config_type: form.config_type,
        metrics: form.metrics,
        ...(form.description.trim() && { description: form.description.trim() }),
      }
      const created = await api.configs.create(payload)
      onCreated(created)
    } catch (e) {
      setError(e.message)
      setSaving(false)
    }
  }

  // close on backdrop click
  function handleBackdrop(e) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={handleBackdrop}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-900">New Configuration</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Application name" required>
              <input
                className={INPUT}
                value={form.application_name}
                onChange={e => set('application_name', e.target.value)}
                placeholder="My App"
                autoFocus
              />
            </Field>
            <Field label="AI model name" required>
              <input
                className={INPUT}
                value={form.ai_model_name}
                onChange={e => set('ai_model_name', e.target.value)}
                placeholder="GPT-4o"
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="AI model type" required>
              <select
                className={INPUT}
                value={form.ai_model_type}
                onChange={e => set('ai_model_type', e.target.value)}
              >
                <option value="">— select —</option>
                {AI_MODEL_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </Field>
            <Field label="Config type" required>
              <select
                className={INPUT}
                value={form.config_type}
                onChange={e => set('config_type', e.target.value)}
              >
                <option value="">— select —</option>
                {CONFIG_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Metric groups" required>
            <div className="grid grid-cols-2 gap-1.5 mt-0.5">
              {METRIC_GROUPS.map(m => (
                <label key={m} className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={form.metrics.includes(m)}
                    onChange={() => toggleMetric(m)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-300"
                  />
                  <span className="text-xs text-gray-700 group-hover:text-gray-900">{m}</span>
                </label>
              ))}
            </div>
          </Field>

          <Field label="Description">
            <textarea
              className={clsx(INPUT, 'resize-none')}
              rows={2}
              value={form.description}
              onChange={e => set('description', e.target.value)}
              placeholder="Optional description…"
            />
          </Field>

          {error && (
            <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-red-700 text-xs">
              <AlertCircle size={12} className="mt-0.5 flex-shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md text-sm font-medium text-gray-600
                       border border-gray-200 hover:bg-white transition-colors"
          >
            Cancel
          </button>
          <button
            disabled={!canSave || saving}
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                       bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {saving
              ? <><Loader2 size={13} className="animate-spin" /> Saving…</>
              : 'Create'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Page ─────────────────────────────────────────────────────

export default function ConfigListPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  function handleCreated(newCfg) {
    queryClient.invalidateQueries({ queryKey: ['configs'] })
    setShowModal(false)
    navigate(`/config/${newCfg.id}/results`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 gap-2 text-gray-400 text-sm">
        <Loader2 size={16} className="animate-spin" />
        Loading configurations…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
        <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
        {error.message}
      </div>
    )
  }

  const configs = data ?? []

  return (
    <div>
      {showModal && (
        <NewConfigModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Configurations</h1>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 tabular-nums">
            {configs.length} {configs.length === 1 ? 'config' : 'configs'}
          </span>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium
                       bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            <Plus size={14} />
            New
          </button>
        </div>
      </div>

      {configs.length === 0 ? (
        <div className="text-center py-20 text-gray-400 text-sm">
          No configurations yet.{' '}
          <button
            onClick={() => setShowModal(true)}
            className="text-indigo-500 hover:text-indigo-700 underline underline-offset-2"
          >
            Create one
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-100">
            <thead>
              <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="px-4 py-3">Application</th>
                <th className="px-4 py-3">AI Model</th>
                <th className="px-4 py-3">Model Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Evaluation Date</th>
                <th className="px-4 py-3 w-24"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {configs.map((cfg) => (
                <tr
                  key={cfg.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/config/${cfg.id}/results`)}
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {cfg.application_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {cfg.ai_model_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                    {cfg.ai_model_type}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={cfg.evaluation_status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 tabular-nums">
                    {formatDate(cfg.evaluation_date)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); navigate(`/config/${cfg.id}/results`) }}
                      className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      View results <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
