import { useEffect, useMemo, useRef, useState } from 'react'
import { Copy, ExternalLink, Link2, QrCode, X, Download, ListChecks } from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'
import clsx from 'clsx'
import { api } from '../services/api'
import QuestionSetEditor from './QuestionSetEditor'

function normalizeText(value) {
  return typeof value === 'string' ? value : ''
}

function buildSurveyUrl({ origin, pilotTag, configId, appVersion, aiModelVersion, schemaId }) {
  const params = new URLSearchParams()
  if (pilotTag.trim()) params.set('pilot_tag', pilotTag.trim())
  if (configId != null) params.set('config_id', String(configId))
  if (appVersion.trim()) params.set('app_version', appVersion.trim())
  if (aiModelVersion.trim()) params.set('ai_model_version', aiModelVersion.trim())
  if (schemaId) params.set('schema_id', String(schemaId))
  return `${origin}/public/survey?${params.toString()}`
}

export default function BuildSurveyLinkModal({ config, schemaId: schemaIdProp, onClose }) {
  const [tab, setTab] = useState('link') // 'link' | 'schema'
  const [pilotTag, setPilotTag] = useState(normalizeText(config?.pilot_tag))
  const [appVersion, setAppVersion] = useState(normalizeText(config?.app_version))
  const [aiModelVersion, setAiModelVersion] = useState(
    normalizeText(config?.ai_model_version || config?.ai_model_name),
  )
  const [copied, setCopied] = useState(false)
  const [schemaId, setSchemaId] = useState(normalizeText(schemaIdProp))
  const [autoAttach, setAutoAttach] = useState(true)
  const qrWrapperRef = useRef(null)

  useEffect(() => {
    setPilotTag(normalizeText(config?.pilot_tag))
    setAppVersion(normalizeText(config?.app_version))
    setAiModelVersion(normalizeText(config?.ai_model_version || config?.ai_model_name))
  }, [config])

  // Auto-attach the latest active question set for this pilot, if any.
  useEffect(() => {
    if (!autoAttach || !pilotTag.trim()) return
    let cancelled = false
    api.survey.schemas.getLatest(pilotTag.trim())
      .then((latest) => { if (!cancelled) setSchemaId(normalizeText(latest?.schema_id)) })
      .catch(() => { if (!cancelled) setSchemaId('') })
    return () => { cancelled = true }
  }, [autoAttach, pilotTag])

  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  const generatedUrl = useMemo(() => buildSurveyUrl({
    origin,
    pilotTag,
    configId: config?.id,
    appVersion,
    aiModelVersion,
    schemaId,
  }), [aiModelVersion, appVersion, config?.id, origin, pilotTag, schemaId])

  async function handleCopy() {
    await navigator.clipboard.writeText(generatedUrl)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  function handleOpen() {
    window.open(generatedUrl, '_blank', 'noopener,noreferrer')
  }

  function handleDownloadQr() {
    const svg = qrWrapperRef.current?.querySelector('svg')
    if (!svg) return

    const serializer = new XMLSerializer()
    const source = serializer.serializeToString(svg)
    const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `survey-qr-config-${config?.id ?? 'link'}.svg`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/40 p-4"
      onClick={(event) => { if (event.target === event.currentTarget) onClose() }}
    >
      <div className="w-full max-w-2xl rounded-2xl bg-white shadow-xl">
        <div className="flex items-start justify-between gap-4 border-b border-gray-100 px-6 py-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Public Survey Link</h2>
            <p className="mt-1 text-sm text-gray-500">
              Share this link with pilot users to answer directly
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex gap-1 border-b border-gray-100 px-6 pt-3">
          <button
            onClick={() => setTab('link')}
            className={clsx(
              'inline-flex items-center gap-1.5 rounded-t-md px-3 py-2 text-sm font-medium transition-colors',
              tab === 'link' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700',
            )}
          >
            <Link2 size={14} /> Link
          </button>
          <button
            onClick={() => setTab('schema')}
            className={clsx(
              'inline-flex items-center gap-1.5 rounded-t-md px-3 py-2 text-sm font-medium transition-colors',
              tab === 'schema' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700',
            )}
          >
            <ListChecks size={14} /> Question Set
          </button>
        </div>

        {tab === 'schema' && (
          <div className="max-h-[70vh] overflow-y-auto px-6 py-5">
            <QuestionSetEditor
              pilotTag={pilotTag}
              onCreated={(schema) => { setSchemaId(schema.schema_id); setAutoAttach(false); setTab('link') }}
            />
          </div>
        )}

        {tab === 'link' && (
        <div className="grid gap-6 px-6 py-5 md:grid-cols-[minmax(0,1fr)_220px]">
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-gray-600">Pilot tag</span>
                <input
                  type="text"
                  value={pilotTag}
                  onChange={(event) => setPilotTag(event.target.value)}
                  className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </label>

              <label className="block">
                <span className="mb-1 block text-xs font-medium text-gray-600">App version</span>
                <input
                  type="text"
                  value={appVersion}
                  onChange={(event) => setAppVersion(event.target.value)}
                  className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-1 block text-xs font-medium text-gray-600">AI model version</span>
                <input
                  type="text"
                  value={aiModelVersion}
                  onChange={(event) => setAiModelVersion(event.target.value)}
                  className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </label>
            </div>

            <div>
              <span className="mb-1 block text-xs font-medium text-gray-600">Configuration</span>
              <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700">
                Config #{config?.id} {'\u2014'} {config?.application_name || 'Unnamed configuration'}
              </div>
            </div>

            <div>
              <div className="mb-1 flex items-center gap-2 text-xs font-medium text-gray-600">
                <Link2 size={13} />
                Generated URL
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  readOnly
                  value={generatedUrl}
                  className="min-w-0 flex-1 rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700"
                />
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                  <Copy size={14} />
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            <div>
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="flex items-center gap-1.5 text-xs font-medium text-gray-600">
                  <ListChecks size={13} /> Question set
                </span>
                <label className="flex items-center gap-1.5 text-xs text-gray-500">
                  <input type="checkbox" checked={autoAttach} onChange={(e) => setAutoAttach(e.target.checked)} />
                  Auto-attach latest for this pilot
                </label>
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={schemaId}
                  onChange={(event) => { setAutoAttach(false); setSchemaId(event.target.value) }}
                  placeholder="No question set attached"
                  className="min-w-0 flex-1 rounded-md border border-gray-200 px-3 py-2 text-sm font-mono text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
                <button
                  onClick={() => setTab('schema')}
                  className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                  <ListChecks size={14} />
                  {schemaId ? 'Edit' : 'Create'}
                </button>
              </div>
              <p className="mt-1 text-xs text-gray-400">
                Respondents will see these questions in addition to SUS &amp; Ethics.
              </p>
            </div>

            <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-800">
              You can also append <code className="rounded bg-white px-1">app_version</code> and{' '}
              <code className="rounded bg-white px-1">ai_model_version</code> to prefill metadata.
            </div>
          </div>

          <div className="space-y-3">
            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
                <QrCode size={16} />
                QR code
              </div>
              <div
                ref={qrWrapperRef}
                className="flex justify-center rounded-lg bg-white p-3"
              >
                <QRCodeSVG value={generatedUrl} size={180} includeMargin />
              </div>
              <button
                onClick={handleDownloadQr}
                className="mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-md border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-white"
              >
                <Download size={14} />
                Download QR
              </button>
            </div>
          </div>
        </div>
        )}

        <div className="flex flex-wrap justify-end gap-3 border-t border-gray-100 px-6 py-4">
          {tab === 'link' && (
            <>
              <button
                onClick={handleOpen}
                className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
              >
                <ExternalLink size={14} />
                OPEN
              </button>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                <Copy size={14} />
                COPY
              </button>
            </>
          )}
          <button
            onClick={onClose}
            className="inline-flex items-center rounded-md border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  )
}
