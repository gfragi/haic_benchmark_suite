import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'
import {
  SUS_QUESTIONS,
  ETHICS_QUESTIONS,
  SCALE_LABELS,
  computeSus,
  makeAnonymousUserId,
} from '../surveyConfig'

function SectionHeader({ title, subtitle }) {
  return (
    <div className="space-y-1">
      <h2 className="text-base font-semibold text-gray-900">{title}</h2>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}

function ScaleQuestion({ questionNum, text, qKey, value, onChange }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <p className="mb-3 text-sm text-gray-800">
        <span className="mr-2 font-mono text-xs text-gray-400">Q{questionNum}</span>
        {text}
      </p>
      <div className="grid grid-cols-5 gap-2">
        {[1, 2, 3, 4, 5].map((n) => (
          <label
            key={n}
            className={clsx(
              'flex cursor-pointer flex-col items-center rounded-lg border px-2 py-2 text-xs transition-colors',
              value === n
                ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 bg-gray-50 text-gray-600 hover:border-gray-300',
            )}
          >
            <input
              type="radio"
              name={qKey}
              value={n}
              checked={value === n}
              onChange={() => onChange(n)}
              className="sr-only"
            />
            <span className="text-sm font-semibold">{n}</span>
            {SCALE_LABELS[n] && (
              <span className="mt-1 text-center text-[10px] leading-tight text-gray-400">
                {SCALE_LABELS[n]}
              </span>
            )}
          </label>
        ))}
      </div>
    </div>
  )
}

function MetaField({ label, value, locked, onChange, placeholder }) {
  return (
    <div className="space-y-1">
      <span className="block text-xs font-medium uppercase tracking-wide text-gray-500">{label}</span>
      {locked ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700">
          {value || '—'}
        </div>
      ) : (
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      )}
    </div>
  )
}

function DomainQuestion({ question, value, onChange }) {
  if (question.type === 'likert') {
    const max = question.scale?.max || 5
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{question.scale?.min_label || '1'}</span>
          <span>{question.scale?.max_label || String(max)}</span>
        </div>
        <div className="grid grid-cols-5 gap-2">
          {Array.from({ length: max }, (_, index) => index + 1).map((item) => (
            <label
              key={item}
              className={clsx(
                'flex cursor-pointer items-center justify-center rounded-lg border px-2 py-2 text-sm font-medium transition-colors',
                value === item
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                  : 'border-gray-200 bg-gray-50 text-gray-600 hover:border-gray-300',
              )}
            >
              <input
                type="radio"
                name={question.id}
                value={item}
                checked={value === item}
                onChange={() => onChange(item)}
                className="sr-only"
              />
              {item}
            </label>
          ))}
        </div>
      </div>
    )
  }

  if (question.type === 'single') {
    return (
      <select
        value={value ?? ''}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
      >
        <option value="">Select an option</option>
        {(question.options || []).map((option) => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    )
  }

  if (question.type === 'multi') {
    const selected = Array.isArray(value) ? value : []
    return (
      <div className="space-y-2">
        {(question.options || []).map((option) => (
          <label key={option} className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={(event) => {
                if (event.target.checked) onChange([...selected, option])
                else onChange(selected.filter((item) => item !== option))
              }}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-300"
            />
            {option}
          </label>
        ))}
      </div>
    )
  }

  if (question.type === 'number') {
    return (
      <input
        type="number"
        value={value ?? ''}
        onChange={(event) => onChange(event.target.value === '' ? null : Number(event.target.value))}
        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
      />
    )
  }

  if (question.type === 'boolean') {
    return (
      <label className="inline-flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(event.target.checked)}
          className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-300"
        />
        Yes
      </label>
    )
  }

  return (
    <textarea
      value={value ?? ''}
      onChange={(event) => onChange(event.target.value)}
      rows={3}
      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
    />
  )
}

export default function PublicSurveyPage() {
  const [searchParams] = useSearchParams()
  const pilotTagParam = searchParams.get('pilot_tag') || ''
  const appVersionParam = searchParams.get('app_version') || ''
  const aiModelVersionParam = searchParams.get('ai_model_version') || ''
  const schemaId = searchParams.get('schema_id') || ''
  const configIdRaw = searchParams.get('config_id')
  const configId = configIdRaw ? Number(configIdRaw) : null

  const [anonymousUserId] = useState(() => makeAnonymousUserId())
  const [pilotTag, setPilotTag] = useState(pilotTagParam)
  const [appVersion, setAppVersion] = useState(appVersionParam)
  const [aiModelVersion, setAiModelVersion] = useState(aiModelVersionParam)
  const [sus, setSus] = useState({})
  const [ethics, setEthics] = useState({})
  const [domainAnswers, setDomainAnswers] = useState({})
  const [comment, setComment] = useState('')
  const [submitError, setSubmitError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState(null)

  const {
    data: schema,
    isLoading: schemaLoading,
    error: schemaError,
  } = useQuery({
    queryKey: ['survey-schema', schemaId],
    queryFn: () => api.survey.schemas.get(schemaId),
    enabled: Boolean(schemaId),
    retry: false,
  })

  const susAnswered = SUS_QUESTIONS.filter((question) => sus[question.key] != null).length
  const ethicsAnswered = ETHICS_QUESTIONS.filter((question) => ethics[question.key] != null).length
  const requiredDomainQuestions = (schema?.questions || []).filter((question) => question.required)
  const missingDomainQuestion = requiredDomainQuestions.find((question) => {
    const value = domainAnswers[question.id]
    if (question.type === 'multi') return !Array.isArray(value) || value.length === 0
    if (question.type === 'boolean') return value == null
    return value == null || value === ''
  })
  const canSubmit = pilotTag.trim() && susAnswered === 10 && ethicsAnswered === 5 && !missingDomainQuestion
  const susScore = computeSus(sus)

  const domainSpecificPayload = useMemo(() => {
    const payload = {}
    if (schema?.questions?.length) {
      for (const question of schema.questions) {
        const value = domainAnswers[question.id]
        if (value != null && value !== '' && (!Array.isArray(value) || value.length > 0)) {
          payload[question.id] = value
        }
      }
    }
    if (comment.trim()) payload.comment = comment.trim()
    return payload
  }, [comment, domainAnswers, schema?.questions])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    setSubmitError(null)

    try {
      await api.survey.submit({
        user_id: anonymousUserId,
        pilot_tag: pilotTag.trim(),
        app_version: appVersion.trim() || undefined,
        ai_model_version: aiModelVersion.trim() || undefined,
        configuration_id: Number.isFinite(configId) ? configId : undefined,
        schema_id: schemaId || undefined,
        tam_sus_responses: sus,
        ethics_responses: ethics,
        domain_specific: Object.keys(domainSpecificPayload).length ? domainSpecificPayload : undefined,
      })
      setSubmitResult({ susScore })
    } catch (error) {
      setSubmitError(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitResult) {
    return (
      <div className="min-h-screen bg-gray-50 px-4 py-10">
        <div className="mx-auto max-w-[600px] rounded-3xl border border-green-200 bg-white px-6 py-10 text-center shadow-sm">
          <CheckCircle2 className="mx-auto h-16 w-16 text-green-500" />
          <h1 className="mt-5 text-2xl font-semibold text-gray-900">Thank you for your feedback.</h1>
          <p className="mt-2 text-sm text-gray-500">Your response has been recorded.</p>
          {submitResult.susScore != null && (
            <div
              className={clsx(
                'mx-auto mt-8 max-w-sm rounded-2xl border px-4 py-5',
                submitResult.susScore >= 70 ? 'border-green-200 bg-green-50 text-green-700'
                  : submitResult.susScore >= 50 ? 'border-amber-200 bg-amber-50 text-amber-700'
                  : 'border-red-200 bg-red-50 text-red-700',
              )}
            >
              <p className="text-sm font-medium">Your usability score: {submitResult.susScore.toFixed(1)} / 100</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-6 sm:py-10">
      <div className="mx-auto max-w-[600px] space-y-6">
        <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
          <h1 className="text-2xl font-semibold text-gray-900">Help us evaluate the platform</h1>
          <p className="mt-2 text-sm text-gray-500">Anonymous · takes ~3 minutes</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
            <SectionHeader title="Metadata" />
            <div className="mt-4 space-y-4">
              <MetaField
                label="Pilot"
                value={pilotTag}
                locked={Boolean(pilotTagParam)}
                onChange={setPilotTag}
                placeholder="Enter pilot tag"
              />
              <MetaField
                label="App version"
                value={appVersion}
                locked={false}
                onChange={setAppVersion}
                placeholder="e.g. v1.2.0"
              />
              <MetaField
                label="AI model"
                value={aiModelVersion}
                locked={false}
                onChange={setAiModelVersion}
                placeholder="e.g. gpt-4.1"
              />
            </div>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
            <SectionHeader
              title="SUS"
              subtitle={`${susAnswered}/10 answered · 1 = Strongly Disagree · 5 = Strongly Agree`}
            />
            <div className="mt-4 space-y-3">
              {SUS_QUESTIONS.map((question, index) => (
                <ScaleQuestion
                  key={question.key}
                  questionNum={index + 1}
                  text={question.text}
                  qKey={question.key}
                  value={sus[question.key] ?? null}
                  onChange={(value) => setSus((current) => ({ ...current, [question.key]: value }))}
                />
              ))}
            </div>

            {susScore != null && (
              <div
                className={clsx(
                  'mt-4 rounded-2xl border px-4 py-3 text-center text-sm font-medium',
                  susScore >= 70 ? 'border-green-200 bg-green-50 text-green-700'
                    : susScore >= 50 ? 'border-amber-200 bg-amber-50 text-amber-700'
                    : 'border-red-200 bg-red-50 text-red-700',
                )}
              >
                Your usability score: {susScore.toFixed(1)} / 100
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
            <SectionHeader
              title="Ethics & Trust"
              subtitle={`${ethicsAnswered}/5 answered · 1 = Strongly Disagree · 5 = Strongly Agree`}
            />
            <div className="mt-4 space-y-3">
              {ETHICS_QUESTIONS.map((question, index) => (
                <ScaleQuestion
                  key={question.key}
                  questionNum={index + 1}
                  text={question.text}
                  qKey={question.key}
                  value={ethics[question.key] ?? null}
                  onChange={(value) => setEthics((current) => ({ ...current, [question.key]: value }))}
                />
              ))}
            </div>
          </div>

          {schemaId && (
            <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
              <SectionHeader title="Additional Questions" subtitle={schema?.name || `Schema ${schemaId}`} />

              {schemaLoading && (
                <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
                  <Loader2 size={14} className="animate-spin" />
                  Loading extra questions…
                </div>
              )}

              {schemaError && (
                <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700">
                  <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
                  {schemaError.message}
                </div>
              )}

              {!!schema?.questions?.length && (
                <div className="mt-4 space-y-4">
                  {schema.questions.map((question, index) => (
                    <div key={question.id} className="rounded-xl border border-gray-200 bg-white p-4">
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-800">
                          {index + 1}. {question.label}
                          {question.required && <span className="ml-1 text-red-500">*</span>}
                        </p>
                        {question.group && (
                          <p className="mt-1 text-xs text-gray-500">{question.group}</p>
                        )}
                      </div>
                      <DomainQuestion
                        question={question}
                        value={domainAnswers[question.id]}
                        onChange={(value) => setDomainAnswers((current) => ({ ...current, [question.id]: value }))}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="rounded-3xl border border-gray-200 bg-white px-5 py-6 shadow-sm sm:px-6">
            <SectionHeader title="Optional Comment" />
            <textarea
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              rows={5}
              placeholder="Any additional feedback?"
              className="mt-4 w-full rounded-2xl border border-gray-200 px-3 py-3 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>

          {submitError && (
            <div className="flex items-start gap-2 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
              {submitError}
            </div>
          )}

          <div className="rounded-3xl border border-gray-200 bg-white px-5 py-5 shadow-sm sm:px-6">
            <button
              type="submit"
              disabled={!canSubmit || submitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {submitting ? <><Loader2 size={16} className="animate-spin" /> Submitting…</> : 'Submit feedback'}
            </button>

            {!canSubmit && !submitting && (
              <p className="mt-3 text-center text-xs text-gray-500">
                {!pilotTag.trim() ? 'Enter a pilot tag to continue.'
                  : susAnswered < 10 ? `Answer all 10 SUS questions (${10 - susAnswered} remaining).`
                  : ethicsAnswered < 5 ? `Answer all 5 ethics questions (${5 - ethicsAnswered} remaining).`
                  : missingDomainQuestion ? `Please answer: ${missingDomainQuestion.label}`
                  : ''}
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
