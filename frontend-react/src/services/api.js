const BASE = '/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  configs: {
    list: (skip = 0, limit = 100) =>
      request(`/configuration/?skip=${skip}&limit=${limit}`),
    get: (id) => request(`/configuration/${id}`),
    create: (body) =>
      request('/configuration/new', { method: 'POST', body: JSON.stringify(body) }),
    update: (id, body) =>
      request(`/configuration/update/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
    delete: (id) =>
      request(`/configuration/delete/${id}`, { method: 'DELETE' }),
  },

  results: {
    list: (configId) => request(`/results/${configId}`),
    get: (configId, resultId) => request(`/results/${configId}/${resultId}`),
    byGroup: (configId, groupName) =>
      request(`/results/${configId}/group/${encodeURIComponent(groupName)}`),
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
    schemas: {
      create: (body) =>
        request('/survey/schemas', { method: 'POST', body: JSON.stringify(body) }),
      getLatest: (pilotTag) => request(`/survey/schemas?pilot_tag=${pilotTag}`),
      get: (schemaId) => request(`/survey/schemas/${schemaId}`),
    },
  },

  health: () => fetch('/meta/health').then((r) => r.json()),
}
