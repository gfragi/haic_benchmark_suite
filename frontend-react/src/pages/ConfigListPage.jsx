import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import { ChevronRight, AlertCircle, Loader2, Plus, X, HelpCircle, Link2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import BuildSurveyLinkModal from '../components/BuildSurveyLinkModal'

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
  pilot_tag: '',
  baseline_s: '',
}

const AI_MODEL_TYPES = [
  'Classification', 'Regression', 'Clustering',
  'XAI', 'Swarm Learning', 'Active Learning', 'Other',
]
const CONFIG_TYPES = ['specific', 'generic']

// ── Field Help Modal ──────────────────────────────────────────

const FIELD_HELP = [
  {
    field: 'Application name',
    plain: 'The name of the system or product you\'re evaluating. This is just a label for your records — it doesn\'t affect computation. Example: "Permit Review Portal" or "Radiology Assist v2".',
  },
  {
    field: 'AI model name',
    plain: 'The identifier of the specific AI model version under evaluation. Use something you\'ll recognise later when comparing results. Example: "GPT-4o", "Gemini 1.5 Pro", "internal-classifier-v3".',
  },
  {
    field: 'AI model type',
    plain: 'The broad algorithmic category of your AI. Choose the type that best describes what the model does: Classification (predicts a category), Regression (predicts a number), XAI (explainable output), Swarm/Active Learning (iterative), or Other.',
  },
  {
    field: 'Config type',
    plain: '"Specific" means this configuration is tied to one exact AI model version — useful when you want to track changes between releases. "Generic" means the configuration applies to the application overall, regardless of model version.',
  },
  {
    field: 'Pilot tag',
    plain: 'Optional. Links this configuration to a pilot field-mapping adapter so the platform knows how to interpret your log format. Example: "smart_energy" or "radiology_v2". Leave blank if you are using the generic log format.',
  },
  {
    field: 'Baseline (seconds)',
    plain: 'Optional. The time in seconds a human would take to complete the same task without AI assistance. Used to compute Effort Loss (EL). Example: 300 means 5 minutes. Leave blank to let the platform auto-derive from your log data (requires 5+ sessions).',
  },
  {
    field: 'Description',
    plain: 'Optional free-text note about this configuration. Useful for recording context like the evaluation date, dataset used, or any deployment conditions that might affect results.',
  },
]

function FieldHelpModal({ onClose }) {
  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">Configuration fields explained</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={16} />
          </button>
        </div>
        <div className="px-6 py-4 space-y-4 max-h-[70vh] overflow-y-auto">
          {FIELD_HELP.map(({ field, plain }) => (
            <div key={field}>
              <p className="text-xs font-semibold text-gray-800 mb-0.5">{field}</p>
              <p className="text-xs text-gray-500 leading-relaxed">{plain}</p>
            </div>
          ))}
        </div>
        <div className="px-6 py-3 border-t border-gray-100 bg-gray-50">
          <button
            onClick={onClose}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

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
  const [showHelp, setShowHelp] = useState(false)

  function set(key, val) {
    setForm(f => ({ ...f, [key]: val }))
  }

  const canSave = form.application_name.trim() && form.ai_model_name.trim()
    && form.ai_model_type && form.config_type

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      const payload = {
        application_name: form.application_name.trim(),
        ai_model_name: form.ai_model_name.trim(),
        ai_model_type: form.ai_model_type,
        config_type: form.config_type,
        metrics: [],
        ...(form.description.trim() && { description: form.description.trim() }),
        ...(form.pilot_tag.trim() && { pilot_tag: form.pilot_tag.trim() }),
        ...(form.baseline_s !== '' && { baseline_s: Number(form.baseline_s) }),
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
        {showHelp && <FieldHelpModal onClose={() => setShowHelp(false)} />}

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-900">New Configuration</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHelp(true)}
              title="What do these fields mean?"
              className="text-gray-300 hover:text-indigo-500 transition-colors"
            >
              <HelpCircle size={15} />
            </button>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
              <X size={16} />
            </button>
          </div>
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

          <div className="grid grid-cols-2 gap-4">
            <Field label="Pilot tag">
              <input
                className={INPUT}
                value={form.pilot_tag}
                onChange={e => set('pilot_tag', e.target.value)}
                placeholder="e.g. smart_energy"
              />
              <p className="text-xs text-gray-400 mt-1">Links to your pilot field mapping adapter</p>
            </Field>
            <Field label="Baseline (seconds)">
              <input
                className={INPUT}
                type="number"
                min="0"
                value={form.baseline_s}
                onChange={e => set('baseline_s', e.target.value)}
                placeholder="e.g. 300"
              />
              <p className="text-xs text-gray-400 mt-1">Seconds for manual-only task. Leave blank for auto-derivation.</p>
            </Field>
          </div>

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
  const [linkConfig, setLinkConfig] = useState(null)

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
      {linkConfig && (
        <BuildSurveyLinkModal
          config={linkConfig}
          onClose={() => setLinkConfig(null)}
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
        <div className="text-center py-20 space-y-3">
          <p className="text-gray-400 text-sm">No configurations yet.</p>
          <div className="flex items-center justify-center gap-4 text-sm">
            <button
              onClick={() => setShowModal(true)}
              className="text-indigo-600 hover:text-indigo-800 underline underline-offset-2 font-medium"
            >
              Create one
            </button>
            <span className="text-gray-300">·</span>
            <Link
              to="/getting-started"
              className="text-gray-500 hover:text-indigo-600 underline underline-offset-2"
            >
              Need help? See the guide
            </Link>
          </div>
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
                <th className="px-4 py-3 w-52"></th>
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
                    <div className="flex items-center justify-end gap-4">
                      <button
                        onClick={(e) => { e.stopPropagation(); setLinkConfig(cfg) }}
                        className="inline-flex items-center gap-1 text-gray-600 hover:text-indigo-700 text-sm font-medium"
                      >
                        <Link2 size={14} />
                        Build Link
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); navigate(`/config/${cfg.id}/results`) }}
                        className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                      >
                        View results <ChevronRight size={14} />
                      </button>
                    </div>
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
