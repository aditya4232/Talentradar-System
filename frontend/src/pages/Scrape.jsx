import { useState, useEffect } from 'react'
import { api } from '../api/client'
import {
  Github, Search, Database, RefreshCw, CheckCircle, XCircle,
  Clock, Play, Zap, AlertCircle, ExternalLink
} from 'lucide-react'

const SOURCES = [
  {
    id: 'github',
    name: 'GitHub',
    icon: Github,
    description: 'Source developers via GitHub API. Finds Indian engineers by location, skills, and open source contributions.',
    color: 'text-white',
    bg: 'bg-gray-800',
    border: 'border-gray-600',
    free: true,
    badge: 'Official API',
    badgeColor: 'bg-green-500/20 text-green-400',
  },
  {
    id: 'naukri',
    name: 'Naukri',
    icon: () => <span className="text-yellow-400 font-bold text-sm">N</span>,
    description: 'Scrape Naukri.com candidate profiles. Requires Playwright browser automation.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-950/30',
    border: 'border-yellow-800',
    free: true,
    badge: 'Browser Scrape',
    badgeColor: 'bg-yellow-500/20 text-yellow-400',
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: () => <span className="text-blue-400 font-bold text-sm">in</span>,
    description: 'Scrape LinkedIn public profiles. Use responsibly with rate limiting.',
    color: 'text-blue-400',
    bg: 'bg-blue-950/30',
    border: 'border-blue-800',
    free: true,
    badge: 'Browser Scrape',
    badgeColor: 'bg-blue-500/20 text-blue-400',
  },
  {
    id: 'mock',
    name: 'Demo Data',
    icon: Database,
    description: 'Generate realistic Indian candidate profiles for testing. No API keys required.',
    color: 'text-brand-400',
    bg: 'bg-brand-950/30',
    border: 'border-brand-700',
    free: true,
    badge: 'Instant',
    badgeColor: 'bg-brand-500/20 text-brand-400',
  },
]

function StatusIcon({ status }) {
  if (status === 'COMPLETED') return <CheckCircle size={14} className="text-green-400" />
  if (status === 'FAILED') return <XCircle size={14} className="text-red-400" />
  if (status === 'RUNNING') return <RefreshCw size={14} className="text-blue-400 animate-spin" />
  return <Clock size={14} className="text-gray-500" />
}

function TriggerModal({ source, onClose, onTrigger }) {
  const [keywords, setKeywords] = useState('Python developer')
  const [location, setLocation] = useState('India')
  const [count, setCount] = useState(20)
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    setLoading(true)
    try {
      await onTrigger(source.id, keywords, location, count)
      onClose()
    } catch (e) {
      console.error(e)
      alert('Failed to start scraping: ' + (e.message || 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="card w-full max-w-md">
        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
          <source.icon size={18} className={source.color} />
          Source from {source.name}
        </h3>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Search Keywords</label>
            <input
              className="input w-full"
              placeholder="e.g. React developer, Python backend, DevOps"
              value={keywords}
              onChange={e => setKeywords(e.target.value)}
            />
            <div className="text-xs text-gray-600 mt-1">Skills, technologies, job titles</div>
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Location</label>
            <input
              className="input w-full"
              placeholder="e.g. India, Bangalore, Mumbai"
              value={location}
              onChange={e => setLocation(e.target.value)}
            />
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Max Candidates</label>
            <input
              type="number"
              className="input w-32"
              min={5}
              max={100}
              value={count}
              onChange={e => setCount(+e.target.value)}
            />
          </div>

          {source.id === 'github' && (
            <div className="bg-green-950/30 border border-green-800 rounded-lg p-3 text-xs text-green-400">
              Uses official GitHub REST API. Set <code className="bg-dark-700 px-1 rounded">GITHUB_TOKEN</code> in .env for higher rate limits.
            </div>
          )}

          {(source.id === 'naukri' || source.id === 'linkedin') && (
            <div className="bg-yellow-950/30 border border-yellow-800 rounded-lg p-3 text-xs text-yellow-400">
              <AlertCircle size={12} className="inline mr-1" />
              Requires Playwright: <code className="bg-dark-700 px-1 rounded">playwright install chromium</code>. Scraping may be blocked; use responsibly.
            </div>
          )}
        </div>

        <div className="flex gap-2 mt-4 justify-end">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleSubmit} disabled={loading} className="btn-primary flex items-center gap-2">
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
            {loading ? 'Starting…' : 'Start Sourcing'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Scrape() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeModal, setActiveModal] = useState(null)
  const [seeding, setSeeding] = useState(false)
  const [pollingIds, setPollingIds] = useState(new Set())

  async function loadHistory() {
    try {
      const data = await api.scrape.history()
      setHistory(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
    const interval = setInterval(loadHistory, 5000)
    return () => clearInterval(interval)
  }, [])

  async function handleTrigger(source, keywords, location, count) {
    const result = await api.scrape.trigger({ source, keywords, location, max_count: count })
    await loadHistory()
  }

  async function handleSeedDemo() {
    setSeeding(true)
    try {
      await api.scrape.seedDemo()
      await loadHistory()
    } catch (e) {
      alert('Seeding failed: ' + (e.message || 'Error'))
    } finally {
      setSeeding(false)
    }
  }

  const runningJobs = history.filter(h => h.status === 'RUNNING')

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Source Candidates</h1>
          <p className="text-gray-500 text-sm mt-1">Aggregate candidates from multiple free sources</p>
        </div>
        <button
          onClick={handleSeedDemo}
          disabled={seeding}
          className="btn-secondary flex items-center gap-2"
        >
          {seeding ? <RefreshCw size={14} className="animate-spin" /> : <Zap size={14} />}
          {seeding ? 'Seeding…' : 'Seed 100 Demo Candidates'}
        </button>
      </div>

      {runningJobs.length > 0 && (
        <div className="bg-blue-950/30 border border-blue-800 rounded-xl p-4 flex items-center gap-3">
          <RefreshCw size={16} className="text-blue-400 animate-spin shrink-0" />
          <div>
            <div className="text-blue-300 font-medium text-sm">
              {runningJobs.length} scraping job{runningJobs.length > 1 ? 's' : ''} running
            </div>
            <div className="text-blue-500 text-xs">Auto-refreshing every 5s…</div>
          </div>
        </div>
      )}

      {/* Source Cards */}
      <div className="grid grid-cols-2 gap-4">
        {SOURCES.map(source => (
          <div key={source.id} className={`card border ${source.border} ${source.bg} hover:opacity-90 transition-opacity`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-dark-800 flex items-center justify-center ${source.color}`}>
                  {typeof source.icon === 'function'
                    ? <source.icon size={20} />
                    : <source.icon size={20} />
                  }
                </div>
                <div>
                  <div className="text-white font-semibold">{source.name}</div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${source.badgeColor}`}>{source.badge}</span>
                </div>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">{source.description}</p>
            <button
              onClick={() => setActiveModal(source)}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Search size={14} />
              Source from {source.name}
            </button>
          </div>
        ))}
      </div>

      {/* Tips */}
      <div className="card bg-dark-800/50">
        <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
          <Zap size={16} className="text-brand-400" /> Quick Tips
        </h3>
        <div className="grid grid-cols-2 gap-3 text-sm text-gray-400">
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span><strong className="text-gray-300">GitHub</strong> is best for developers (uses official API, no limits with token)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span><strong className="text-gray-300">Demo Data</strong> seeds 100 realistic Indian candidates instantly for testing</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span>Candidates are <strong className="text-gray-300">deduplicated by email</strong> — no duplicates in DB</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span><strong className="text-gray-300">TalentScore</strong> is auto-computed on ingestion using AI engine</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span>Set <code className="bg-dark-700 px-1 rounded text-xs">GROQ_API_KEY</code> in .env for enhanced AI scoring</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-brand-400 mt-0.5">→</span>
            <span>After sourcing, go to a <strong className="text-gray-300">Job</strong> to see ranked candidates</span>
          </div>
        </div>
      </div>

      {/* Scraping History */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-white">Scraping History</h3>
          <button onClick={loadHistory} className="text-gray-500 hover:text-gray-300">
            <RefreshCw size={14} />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-600">Loading…</div>
        ) : history.length === 0 ? (
          <div className="text-center py-12 text-gray-600">
            <Database size={32} className="mx-auto mb-3 opacity-30" />
            <div>No scraping jobs yet.</div>
            <div className="text-sm mt-1">Start by seeding demo data or sourcing from GitHub.</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Source</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Keywords</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Location</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Status</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Found</th>
                  <th className="text-left text-gray-500 font-medium pb-2">Started</th>
                </tr>
              </thead>
              <tbody>
                {history.map(job => (
                  <tr key={job.id} className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors">
                    <td className="py-2.5 pr-4">
                      <span className="badge bg-dark-700 text-gray-300 uppercase text-xs">{job.source}</span>
                    </td>
                    <td className="py-2.5 pr-4 text-gray-400 max-w-32 truncate">{job.keywords || '—'}</td>
                    <td className="py-2.5 pr-4 text-gray-500">{job.location || '—'}</td>
                    <td className="py-2.5 pr-4">
                      <div className="flex items-center gap-1.5">
                        <StatusIcon status={job.status} />
                        <span className={`text-xs ${
                          job.status === 'COMPLETED' ? 'text-green-400' :
                          job.status === 'FAILED' ? 'text-red-400' :
                          job.status === 'RUNNING' ? 'text-blue-400' : 'text-gray-500'
                        }`}>{job.status}</span>
                      </div>
                      {job.error_message && (
                        <div className="text-xs text-red-500 mt-0.5 truncate max-w-48">{job.error_message}</div>
                      )}
                    </td>
                    <td className="py-2.5 pr-4">
                      {job.profiles_found > 0
                        ? <span className="text-green-400 font-medium">{job.profiles_found}</span>
                        : <span className="text-gray-600">—</span>
                      }
                    </td>
                    <td className="py-2.5 text-gray-600 text-xs">
                      {job.started_at ? new Date(job.started_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {activeModal && (
        <TriggerModal
          source={activeModal}
          onClose={() => setActiveModal(null)}
          onTrigger={handleTrigger}
        />
      )}
    </div>
  )
}
