import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { PlayCircle, Loader2, CheckCircle2, AlertTriangle, ChevronRight } from 'lucide-react'
import { api } from '../services/api'

export default function SimulatePage() {
  const navigate = useNavigate()

  const { data: scenarios, isLoading: scenariosLoading } = useQuery({
    queryKey: ['simulate-scenarios'],
    queryFn: () => api.simulate.scenarios(),
  })

  const { data: configs, isLoading: configsLoading } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  const [scenarioId, setScenarioId] = useState('')
  const [configurationId, setConfigurationId] = useState('')
  const [pilotTag, setPilotTag] = useState('')
  const [appVersion, setAppVersion] = useState('sim_v1.0.0')
  const [aiModelVersion, setAiModelVersion] = useState('sim-1.0')
  const [runs, setRuns] = useState(5)

  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [evaluating, setEvaluating] = useState(false)

  const scenarioList = scenarios?.scenarios ?? []
  const selectedScenario = scenarioList.find((s) => s.id === scenarioId)

  function handleScenarioChange(id) {
    setScenarioId(id)
    const scenario = scenarioList.find((s) => s.id === id)
    if (scenario) setPilotTag(scenario.suggested_pilot_tag)
  }

  const canRun = scenarioId && configurationId && pilotTag.trim() && runs >= 1

  async function handleRun() {
    if (!canRun) return
    setRunning(true)
    setError(null)
    setResult(null)
    try {
      const out = await api.simulate.run({
        configurationId: Number(configurationId),
        name: `${scenarioId}.yaml`,
        pilotTag: pilotTag.trim(),
        appVersion: appVersion.trim(),
        aiModelVersion: aiModelVersion.trim(),
        runs: Number(runs),
      })
      setResult(out)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  async function handleEvaluate() {
    setEvaluating(true)
    try {
      await api.evaluate.trigger(configurationId)
      navigate(`/config/${configurationId}/results`)
    } catch (e) {
      setError(e.message)
      setEvaluating(false)
    }
  }

  return (
    <div className="space-y-5 max-w-2xl">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">Simulate</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Generate synthetic sessions from a scripted scenario and ingest them into a
          configuration, the same way real pilot data is uploaded. Useful for populating a
          pilot before real data arrives, or exercising the evaluation pipeline end-to-end.
        </p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Scenario</label>
          {scenariosLoading && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Loader2 size={14} className="animate-spin" /> Loading scenarios…
            </div>
          )}
          {!scenariosLoading && (
            <select
              value={scenarioId}
              onChange={(e) => handleScenarioChange(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
            >
              <option value="">Choose a scenario…</option>
              {scenarioList.map((s) => (
                <option key={s.id} value={s.id}>{s.label}</option>
              ))}
            </select>
          )}
          {selectedScenario && !selectedScenario.has_human_agent && (
            <p className="mt-1.5 flex items-center gap-1 text-xs text-amber-600">
              <AlertTriangle size={12} /> This scenario has no human agent — it's a
              multi-AI-agent demo, not a human-AI collaboration scenario.
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Target configuration</label>
          {configsLoading && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Loader2 size={14} className="animate-spin" /> Loading configurations…
            </div>
          )}
          {!configsLoading && (
            <select
              value={configurationId}
              onChange={(e) => setConfigurationId(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
            >
              <option value="">Choose a configuration…</option>
              {(configs ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  #{c.id} — {c.application_name}{c.pilot_tag ? ` (${c.pilot_tag})` : ''}
                </option>
              ))}
            </select>
          )}
          <Link to="/configs" className="mt-1 inline-flex items-center gap-0.5 text-xs text-indigo-600 hover:text-indigo-800">
            Need a new one? Create it on the Evaluations page <ChevronRight size={12} />
          </Link>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Pilot tag</label>
            <input
              type="text"
              value={pilotTag}
              onChange={(e) => setPilotTag(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Number of runs</label>
            <input
              type="number"
              min={1}
              max={200}
              value={runs}
              onChange={(e) => setRuns(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">App version</label>
            <input
              type="text"
              value={appVersion}
              onChange={(e) => setAppVersion(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">AI model version</label>
            <input
              type="text"
              value={aiModelVersion}
              onChange={(e) => setAiModelVersion(e.target.value)}
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
        </div>

        <p className="text-xs text-gray-400">
          Each run currently replays the same scripted scenario with a different seed —
          expect limited variance across sessions until parameterized/dataset-driven scenarios
          are added.
        </p>

        <button
          onClick={handleRun}
          disabled={!canRun || running}
          className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {running ? <Loader2 size={14} className="animate-spin" /> : <PlayCircle size={14} />}
          {running ? 'Running…' : 'Generate & Ingest'}
        </button>

        {error && (
          <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" /> {error}
          </div>
        )}

        {result && (
          <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700 space-y-2">
            <p className="flex items-center gap-1.5 font-medium">
              <CheckCircle2 size={14} /> {result.detail}
            </p>
            {result.schema_warnings?.length > 0 && (
              <p className="text-xs text-amber-700">
                {result.schema_warnings.length} schema warning(s) — check the ingested data.
              </p>
            )}
            <button
              onClick={handleEvaluate}
              disabled={evaluating}
              className="inline-flex items-center gap-1.5 rounded-md border border-green-300 bg-white px-3 py-1.5 text-xs font-medium text-green-700 transition-colors hover:bg-green-100 disabled:opacity-50"
            >
              {evaluating && <Loader2 size={12} className="animate-spin" />}
              Run Evaluation & View Results
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
