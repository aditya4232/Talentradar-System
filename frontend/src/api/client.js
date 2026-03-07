const BASE = '/api'

async function request(method, path, body, params) {
  let url = BASE + path
  if (params) {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== ''))
    if (qs.toString()) url += '?' + qs.toString()
  }
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(url, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Jobs
  jobs: {
    list: (params) => request('GET', '/jobs', undefined, params),
    get: (id) => request('GET', `/jobs/${id}`),
    create: (data) => request('POST', '/jobs', data),
    update: (id, data) => request('PUT', `/jobs/${id}`, data),
    delete: (id) => request('DELETE', `/jobs/${id}`),
    parseJD: (id) => request('POST', `/jobs/${id}/parse-jd`),
  },
  // Candidates
  candidates: {
    list: (params) => request('GET', '/candidates', undefined, params),
    count: () => request('GET', '/candidates/count'),
    get: (id) => request('GET', `/candidates/${id}`),
    create: (data) => request('POST', '/candidates', data),
    update: (id, data) => request('PUT', `/candidates/${id}`, data),
    delete: (id) => request('DELETE', `/candidates/${id}`),
    searchForJob: (jobId, limit) => request('POST', `/candidates/search-for-job/${jobId}`, undefined, { limit }),
    brief: (candidateId, jobId) => request('GET', `/candidates/${candidateId}/brief/${jobId}`),
  },
  // Pipeline
  pipeline: {
    board: (jobId) => request('GET', `/pipeline/board/${jobId}`),
    add: (params) => request('POST', '/pipeline/add', undefined, params),
    move: (entryId, stage, notes) => request('PUT', `/pipeline/move/${entryId}`, undefined, { stage, notes }),
    remove: (entryId) => request('DELETE', `/pipeline/${entryId}`),
    candidatePipelines: (candidateId) => request('GET', `/pipeline/candidate/${candidateId}`),
  },
  // Outreach
  outreach: {
    generateEmail: (params) => request('POST', '/outreach/generate-email', undefined, params),
    send: (params) => request('POST', '/outreach/send', undefined, params),
    history: (candidateId) => request('GET', `/outreach/history/${candidateId}`),
  },
  // Analytics
  analytics: {
    dashboard: () => request('GET', '/analytics/dashboard'),
    funnel: (jobId) => request('GET', `/analytics/funnel/${jobId}`),
    sourceEffectiveness: () => request('GET', '/analytics/source-effectiveness'),
    topCandidates: (limit) => request('GET', '/analytics/top-candidates', undefined, { limit }),
  },
  // Scraping
  scrape: {
    trigger: (params) => request('POST', '/scrape/trigger', undefined, params),
    status: (id) => request('GET', `/scrape/status/${id}`),
    history: () => request('GET', '/scrape/history'),
    seedDemo: (count) => request('POST', '/scrape/seed-demo', undefined, { count }),
  },
}
