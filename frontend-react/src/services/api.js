const BASE = '/api/v1'

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (window.__kc?.authenticated && window.__kc?.token) {
    headers.Authorization = `Bearer ${window.__kc.token}`
  }
  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    const detail = err.detail
    // ErrorEnvelope shape from app.utils.errors.http_error():
    // {"detail": {"error": {"code": ..., "message": ...}}}
    const msg = Array.isArray(detail)
      ? detail.map(e => `${e.loc?.slice(-1)[0] ?? ''}: ${e.msg}`).join('; ')
      : (detail?.error?.message ?? (typeof detail === 'string' ? detail : null) ?? `HTTP ${res.status}`)
    const thrown = new Error(msg)
    thrown.code = Array.isArray(detail) ? undefined : detail?.error?.code
    throw thrown
  }
  return res.json()
}

export const api = {
  configs: {
    list: (skip = 0, limit = 100) =>
      request(`/configuration/list?skip=${skip}&limit=${limit}`),
    get: (id) => request(`/configuration/${id}`),
    create: (body) =>
      request('/configuration/new', { method: 'POST', body: JSON.stringify(body) }),
    update: (id, body) =>
      request(`/configuration/update/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
    delete: (id) =>
      request(`/configuration/delete/${id}`, { method: 'DELETE' }),
    purge: (id) =>
      request(`/configuration/${id}/purge`, { method: 'POST' }),
    setSchema: (id, schemaId) =>
      request(`/configuration/${id}/schema`, { method: 'PATCH', body: JSON.stringify({ schema_id: schemaId }) }),
  },

  results: {
    list: (configId) => request(`/results/${configId}`),
    get: (configId, resultId) => request(`/results/${configId}/${resultId}`),
    byGroup: (configId, groupName) =>
      request(`/results/${configId}/group/${encodeURIComponent(groupName)}`),
    holistic: (configId) => request(`/results/${configId}/holistic`),
  },

  logs: {
    list: (configId) => request(`/logs/${configId}`),
    upload: (configId, file) => {
      const fd = new FormData()
      fd.append('file', file)
      return fetch(`${BASE}/logs/upload?configuration_id=${configId}`, {
        method: 'POST',
        body: fd,
      }).then((r) => {
        if (!r.ok) return r.json().then((e) => Promise.reject(new Error(e.detail ?? `HTTP ${r.status}`)))
        return r.json()
      })
    },
    uploadZip: (configId, file) => {
      const fd = new FormData()
      fd.append('file', file)
      return fetch(`${BASE}/logs/upload-zip?configuration_id=${configId}`, {
        method: 'POST',
        body: fd,
      }).then((r) => {
        if (!r.ok) return r.json().then((e) => Promise.reject(new Error(e.detail ?? `HTTP ${r.status}`)))
        return r.json()
      })
    },
    register: (configId, body) =>
      request(`/logs/register?configuration_id=${configId}`, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    downloadUrl: (configId, objectKey) =>
      request(`/logs/download/${configId}?object_key=${encodeURIComponent(objectKey)}`),
    remove: (configId, logName) =>
      request(`/logs/${configId}/${encodeURIComponent(logName)}`, { method: 'DELETE' }),
  },

  // Pull-based ingestion: register a partner-owned HTTP endpoint we poll on
  // a schedule instead of requiring a manual upload every time. Separate
  // from logs.register above, which pushes one already-complete session log.
  polledSources: {
    list: (configId) => request(`/logs/polled-sources?configuration_id=${configId}`),
    register: (configId, body) =>
      request(`/logs/polled-sources?configuration_id=${configId}`, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    remove: (sourceId) => request(`/logs/polled-sources/${sourceId}`, { method: 'DELETE' }),
    pollNow: (sourceId) => request(`/logs/polled-sources/${sourceId}/poll-now`, { method: 'POST' }),
  },

  evaluate: {
    trigger: (configId) =>
      request(`/evaluate/${configId}`, { method: 'POST' }),
  },

  reporting: {
    aggregateByDate: () => request('/reporting/aggregate-by-date'),
    timeSeries: () => request('/reporting/time-series-data'),
    generateReport: () => request('/reporting/generate-report'),
  },

  analytics: {
    latencyPctiles: (configId, params = {}) => {
      const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null))
      return request(`/analytics/latency/pctiles/${configId}?${qs}`)
    },
    humanRtPctiles: (configId, params = {}) => {
      const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null))
      return request(`/analytics/human_rt/pctiles/${configId}?${qs}`)
    },
  },

  survey: {
    submit: (body) => request('/survey', { method: 'POST', body: JSON.stringify(body) }),
    aggregate: (pilotTag) =>
      request(`/survey/aggregate${pilotTag ? `?pilot_tag=${pilotTag}` : ''}`),
    versions: (pilotTag) => request(`/survey/versions?pilot_tag=${pilotTag}`),
    summary: (pilotTag, appVersion) =>
      request(`/survey/summary?pilot_tag=${pilotTag}&app_version=${appVersion}`),
    compare: (pilotTag, versionA, versionB) =>
      request(`/survey/compare?pilot_tag=${pilotTag}&version_a=${versionA}&version_b=${versionB}`),
    questionAverages: (pilotTag, appVersion) =>
      request(`/survey/question-averages?pilot_tag=${pilotTag}&app_version=${appVersion}`),
    domainSpecificAverages: (pilotTag, appVersion) =>
      request(`/survey/domain-specific-averages?pilot_tag=${pilotTag}&app_version=${appVersion}`),
    comments: (pilotTag, appVersion) =>
      request(`/survey/comments?pilot_tag=${pilotTag}${appVersion ? `&app_version=${appVersion}` : ''}`),
    raw: (pilotTag, appVersion) =>
      request(`/survey/raw?pilot_tag=${pilotTag}${appVersion ? `&app_version=${appVersion}` : ''}`),
    schemas: {
      create: (body) =>
        request('/survey/schemas', { method: 'POST', body: JSON.stringify(body) }),
      getLatest: (pilotTag) => request(`/survey/schemas?pilot_tag=${pilotTag}`),
      get: (schemaId) => request(`/survey/schemas/${schemaId}`),
    },
  },

  fairness: {
    evaluateFromLog: (payload) =>
      request('/fairness/evaluate-from-log/', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },

  interpret: (body) =>
    request('/interpret', { method: 'POST', body: JSON.stringify(body) }),

  adapters: {
    // GET /meta/adapters — list all registered adapter tags
    list: () => fetch('/meta/adapters').then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      return r.json()
    }),
    // GET /api/v1/adapters/{tag} — fetch saved config for one adapter
    getConfig: (tag) => request(`/adapters/${encodeURIComponent(tag)}`),
    // POST /api/v1/adapters/register — save + activate a field-mapping config
    register: (body) =>
      request('/adapters/register', { method: 'POST', body: JSON.stringify(body) }),
    // POST /api/v1/adapters/test — test mapping on a sample event dict
    test: (body) =>
      request('/adapters/test', { method: 'POST', body: JSON.stringify(body) }),
  },

  pilot: {
    onboard: (body) =>
      request('/pilot/onboard', { method: 'POST', body: JSON.stringify(body) }),
  },

  envBuilder: {
    listConfigs: () => request('/env/list_configs'),
    loadConfig: (name) => request(`/env/load_config?name=${encodeURIComponent(name)}`),
    generateConfig: (body) =>
      request('/env/generate_config', { method: 'POST', body: JSON.stringify(body) }),
  },

  simulate: {
    scenarios: () => request('/simulator/scenarios'),
    run: ({ configurationId, name, pilotTag, appVersion, aiModelVersion, runs, seed }) => {
      const params = new URLSearchParams({
        configuration_id: String(configurationId),
        name,
        pilot_tag: pilotTag,
        app_version: appVersion,
        ai_model_version: aiModelVersion,
        runs: String(runs),
        seed: String(seed ?? 0),
      })
      return request(`/simulator/simulate-and-ingest?${params.toString()}`, { method: 'POST' })
    },
    // POST /simulator/probabilistic - body matches SimulateProbabilisticRequest field-for-field
    runProbabilistic: (body) =>
      request('/simulator/probabilistic', { method: 'POST', body: JSON.stringify(body) }),
  },

  ontology: {
    get: () => request('/ontology'),
    templates: () => request('/ontology/templates'),
    // POST /ontology/fit-model - multipart. formData is built by the
    // caller (file + domain + label + mapping fields), same pattern as
    // logs.upload/logs.uploadZip above.
    fitModel: (formData) =>
      fetch(`${BASE}/ontology/fit-model`, { method: 'POST', body: formData }).then((r) => {
        if (!r.ok) return r.json().then((e) => {
          const detail = e.detail
          const msg = Array.isArray(detail)
            ? detail.map((d) => `${d.loc?.slice(-1)[0] ?? ''}: ${d.msg}`).join('; ')
            : (detail?.error?.message ?? detail ?? `HTTP ${r.status}`)
          const err = new Error(msg)
          // preserve the backend's error code (e.g. NO_VALID_PAIRS,
          // INSUFFICIENT_DATA) so callers can branch on it instead of
          // matching against message text
          err.code = Array.isArray(detail) ? undefined : detail?.error?.code
          return Promise.reject(err)
        })
        return r.json()
      }),
  },

  health: () => fetch('/meta/health').then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    return r.json()
  }),
}
