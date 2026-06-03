import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import { SUS_QUESTIONS, ETHICS_QUESTIONS, SCALE_LABELS, computeSus } from '../surveyConfig'

function RadioRow({ questionNum, text, qKey, value, onChange }) {
  return (
    <div className="grid grid-cols-5 gap-2 py-3 border-b border-gray-100 last:border-0 items-start">
      <div className="col-span-3">
        <span className="text-xs text-gray-400 font-mono mr-1.5">Q{questionNum}</span>
        <span className="text-sm text-gray-700">{text}</span>
      </div>
      <div className="col-span-2">
        <div className="flex items-center justify-between gap-1">
          {[1, 2, 3, 4, 5].map(n => (
            <label
              key={n}
              className="flex flex-col items-center gap-0.5 cursor-pointer flex-1"
            >
              <input
                type="radio"
                name={qKey}
                value={n}
                checked={value === n}
                onChange={() => onChange(n)}
                className="text-indigo-600 focus:ring-indigo-300 cursor-pointer"
              />
              <span className="text-xs text-gray-400">{n}</span>
              {SCALE_LABELS[n] && (
                <span className="text-xs text-gray-300 text-center leading-tight" style={{ fontSize: '9px' }}>
                  {SCALE_LABELS[n]}
                </span>
              )}
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}

function SectionHeader({ number, title }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold flex items-center justify-center flex-shrink-0">
        {number}
      </span>
      <h2 className="text-sm font-semibold text-gray-800">{title}</h2>
    </div>
  )
}

export default function SurveyPage() {
  const [searchParams] = useSearchParams()
  const configIdFromUrl = searchParams.get('config_id') ? Number(searchParams.get('config_id')) : null

  const [selectedConfigId, setSelectedConfigId] = useState(configIdFromUrl)
  const [userId, setUserId] = useState('')
  const [pilotTag, setPilotTag] = useState('')
  const [appVersion, setAppVersion] = useState('')
  const [sus, setSus] = useState({})
  const [ethics, setEthics] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState(null)
  const [submitError, setSubmitError] = useState(null)

  const { data: configs } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
    enabled: configIdFromUrl == null,
  })

  const { data: linkedConfig } = useQuery({
    queryKey: ['config', selectedConfigId],
    queryFn: () => api.configs.get(selectedConfigId),
    enabled: selectedConfigId != null,
  })

  useEffect(() => {
    if (linkedConfig && !pilotTag) setPilotTag(linkedConfig.application_name ?? '')
    if (linkedConfig && !appVersion) setAppVersion(linkedConfig.ai_model_name ?? '')
  }, [linkedConfig])

  const susScore = computeSus(sus)
  const susAnswered = SUS_QUESTIONS.filter(q => sus[q.key] != null).length
  const ethicsAnswered = ETHICS_QUESTIONS.filter(q => ethics[q.key] != null).length
  const canSubmit = userId.trim() && pilotTag.trim() && susAnswered === 10 && ethicsAnswered === 5

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return
    setSubmitting(true)
    setSubmitError(null)
    try {
      const result = await api.survey.submit({
        user_id: userId.trim(),
        pilot_tag: pilotTag.trim(),
        app_version: appVersion.trim() || undefined,
        configuration_id: selectedConfigId || undefined,
        tam_sus_responses: sus,
        ethics_responses: ethics,
      })
      setSubmitResult({ ...result, susScore })
    } catch (e) {
      setSubmitError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitResult) {
    const score = submitResult.susScore
    return (
      <div className="max-w-xl mx-auto space-y-5 py-8">
        <div className="rounded-xl border border-green-200 bg-green-50 p-8 flex flex-col items-center gap-4 text-center">
          <CheckCircle2 size={36} className="text-green-500" />
          <div>
            <p className="text-base font-semibold text-green-800">Survey submitted — thank you!</p>
            {score != null && (
              <p className={clsx(
                'text-3xl font-bold mt-3',
                score >= 70 ? 'text-green-600' : score >= 50 ? 'text-amber-500' : 'text-red-500',
              )}>
                {score.toFixed(1)} / 100
              </p>
            )}
            {score != null && (
              <p className="text-xs text-gray-500 mt-1">
                {score >= 70 ? 'Good usability' : score >= 50 ? 'Marginal usability' : 'Poor usability — consider UX improvements'}
              </p>
            )}
          </div>
          {selectedConfigId && (
            <Link
              to={`/config/${selectedConfigId}/results`}
              className="text-sm text-indigo-600 hover:text-indigo-800 underline"
            >
              View results for this configuration
            </Link>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-base font-semibold text-gray-900">Submit Survey</h1>
        <p className="text-xs text-gray-400 mt-0.5">SUS usability + ethics assessment</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* Section 1 — Config link (only when not in URL) */}
        {configIdFromUrl == null && (
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <SectionHeader number="1" title="Configuration link (optional)" />
            <div className="space-y-1.5">
              <select
                value={selectedConfigId ?? ''}
                onChange={e => setSelectedConfigId(e.target.value ? Number(e.target.value) : null)}
                className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700
                           focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
              >
                <option value="">— No configuration (standalone) —</option>
                {(configs ?? []).map(c => (
                  <option key={c.id} value={c.id}>
                    {c.application_name}{c.ai_model_name ? ` — ${c.ai_model_name}` : ''}{c.evaluation_status ? ` — ${c.evaluation_status}` : ''}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-400">
                Linking lets you see SUS results in the Holistic tab
              </p>
            </div>
          </div>
        )}

        {/* Section 2 — Respondent info */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <SectionHeader number={configIdFromUrl == null ? '2' : '1'} title="Respondent info" />
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">User ID</label>
              <input
                type="text"
                value={userId}
                onChange={e => setUserId(e.target.value)}
                placeholder="anonymous identifier"
                required
                className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Pilot tag</label>
              <input
                type="text"
                value={pilotTag}
                onChange={e => setPilotTag(e.target.value)}
                placeholder="e.g. energy, applications"
                required
                className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">App version (optional)</label>
              <input
                type="text"
                value={appVersion}
                onChange={e => setAppVersion(e.target.value)}
                placeholder="e.g. v2.1"
                className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
          </div>
        </div>

        {/* Section 3 — SUS Questions */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <SectionHeader number={configIdFromUrl == null ? '3' : '2'} title="System Usability Scale (SUS)" />
            <span className="text-xs text-gray-400">{susAnswered}/10 answered</span>
          </div>

          <div className="text-xs text-gray-400 mb-3 flex justify-end gap-8 pr-1">
            <span>1 = Strongly Disagree</span>
            <span>5 = Strongly Agree</span>
          </div>

          <div>
            {SUS_QUESTIONS.map((q, i) => (
              <RadioRow
                key={q.key}
                questionNum={i + 1}
                text={q.text}
                qKey={q.key}
                value={sus[q.key] ?? null}
                onChange={v => setSus(prev => ({ ...prev, [q.key]: v }))}
              />
            ))}
          </div>

          {susScore != null && (
            <div className={clsx(
              'mt-4 px-4 py-2.5 rounded-lg text-sm font-semibold text-center',
              susScore >= 70 ? 'bg-green-50 text-green-700 border border-green-200'
              : susScore >= 50 ? 'bg-amber-50 text-amber-700 border border-amber-200'
              : 'bg-red-50 text-red-700 border border-red-200',
            )}>
              Your SUS score: {susScore.toFixed(1)} / 100
            </div>
          )}
        </div>

        {/* Section 4 — Ethics & Trust */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <SectionHeader number={configIdFromUrl == null ? '4' : '3'} title="Ethics & Trust" />
            <span className="text-xs text-gray-400">{ethicsAnswered}/5 answered</span>
          </div>

          <div className="text-xs text-gray-400 mb-3 flex justify-end gap-8 pr-1">
            <span>1 = Strongly Disagree</span>
            <span>5 = Strongly Agree</span>
          </div>

          <div>
            {ETHICS_QUESTIONS.map((q, i) => (
              <RadioRow
                key={q.key}
                questionNum={i + 1}
                text={q.text}
                qKey={q.key}
                value={ethics[q.key] ?? null}
                onChange={v => setEthics(prev => ({ ...prev, [q.key]: v }))}
              />
            ))}
          </div>
        </div>

        {/* Error */}
        {submitError && (
          <div className="flex items-start gap-2 rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
            <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
            {submitError}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={!canSubmit || submitting}
          className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-lg text-sm
                     font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {submitting
            ? <><Loader2 size={14} className="animate-spin" /> Submitting…</>
            : 'Submit Survey'}
        </button>

        {!canSubmit && !submitting && (
          <p className="text-xs text-gray-400 text-center -mt-2">
            {!userId.trim() ? 'Enter a user ID to continue.'
              : !pilotTag.trim() ? 'Enter a pilot tag to continue.'
              : susAnswered < 10 ? `Answer all 10 SUS questions (${10 - susAnswered} remaining).`
              : `Answer all 5 ethics questions (${5 - ethicsAnswered} remaining).`}
          </p>
        )}
      </form>
    </div>
  )
}
