import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { Briefcase, Users, TrendingUp, Target, AlertTriangle, Trophy, Clock, ArrowRight } from 'lucide-react'
import TalentScoreBadge from '../components/TalentScoreBadge'
import StageBadge from '../components/StageBadge'

function StatCard({ icon: Icon, label, value, sub, color = 'brand' }) {
  const colors = {
    brand: 'text-brand-400 bg-brand-400/10',
    green: 'text-green-400 bg-green-400/10',
    yellow: 'text-yellow-400 bg-yellow-400/10',
    red: 'text-red-400 bg-red-400/10',
    teal: 'text-teal-400 bg-teal-400/10',
  }
  return (
    <div className="card flex items-start gap-4">
      <div className={`p-2.5 rounded-lg ${colors[color]}`}>
        <Icon size={20} />
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-gray-400">{label}</div>
        {sub && <div className="text-xs text-gray-500 mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [topCandidates, setTopCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)

  useEffect(() => {
    Promise.all([api.analytics.dashboard(), api.analytics.topCandidates(5)])
      .then(([dash, top]) => { setData(dash); setTopCandidates(top) })
      .finally(() => setLoading(false))
  }, [])

  const handleSeedDemo = async () => {
    setSeeding(true)
    try {
      await api.scrape.seedDemo(100)
      setTimeout(() => window.location.reload(), 2000)
    } catch { setSeeding(false) }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-2 border-brand-500 border-t-transparent" />
    </div>
  )

  const stats = data?.stats || {}
  const activity = data?.recent_activity || []
  const sources = data?.source_breakdown || {}

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">TalentRadar AI — Zero-cost Recruitment OS</p>
        </div>
        {stats.total_candidates === 0 && (
          <button onClick={handleSeedDemo} disabled={seeding} className="btn-primary flex items-center gap-2">
            {seeding ? '⏳ Seeding...' : '🚀 Seed 100 Demo Candidates'}
          </button>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard icon={Briefcase} label="Open Jobs" value={stats.open_jobs ?? 0} sub={`${stats.total_jobs ?? 0} total`} color="brand" />
        <StatCard icon={Users} label="Candidates" value={stats.total_candidates ?? 0} sub={`+${stats.new_candidates_this_week ?? 0} this week`} color="teal" />
        <StatCard icon={Trophy} label="Placements" value={stats.placements ?? 0} sub={`${stats.offers_in_progress ?? 0} offers in progress`} color="green" />
        <StatCard icon={AlertTriangle} label="SLA At Risk" value={stats.sla_at_risk ?? 0} sub="Jobs near deadline" color={stats.sla_at_risk > 0 ? "red" : "green"} />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <StatCard icon={Target} label="Avg TalentScore" value={`${stats.avg_talent_score ?? 0}/100`} color="brand" />
        <StatCard icon={TrendingUp} label="Interviews" value={stats.interviews_scheduled ?? 0} sub="Active interviews" color="yellow" />
        <StatCard icon={Clock} label="Pipeline" value={stats.total_pipeline_entries ?? 0} sub="Total entries" color="teal" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <h2 className="font-semibold text-white mb-4">Recent Pipeline Activity</h2>
          {activity.length === 0 ? (
            <p className="text-gray-500 text-sm">No activity yet. Create a job and add candidates.</p>
          ) : (
            <div className="space-y-3">
              {activity.map((a, i) => (
                <div key={i} className="flex items-start gap-3 py-2 border-b border-dark-700 last:border-0">
                  <div className="w-8 h-8 rounded-full bg-brand-600/20 flex items-center justify-center text-brand-400 text-xs font-bold shrink-0">
                    {a.candidate[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-gray-200 truncate">{a.candidate}</div>
                    <div className="text-xs text-gray-500 truncate">{a.job} · {a.company}</div>
                  </div>
                  <StageBadge stage={a.stage} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Source breakdown */}
        <div className="card">
          <h2 className="font-semibold text-white mb-4">Candidate Sources</h2>
          {Object.keys(sources).length === 0 ? (
            <p className="text-gray-500 text-sm">No sourcing data yet. Run a scraping job.</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(sources).slice(0, 6).map(([src, count]) => {
                const total = Object.values(sources).reduce((a, b) => a + b, 0)
                const pct = Math.round(count / total * 100)
                return (
                  <div key={src}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize text-gray-300">{src}</span>
                      <span className="text-gray-400">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 bg-dark-700 rounded-full">
                      <div className="h-full bg-brand-600 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Top Candidates */}
      {topCandidates.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Top Candidates by TalentScore</h2>
            <Link to="/candidates" className="text-brand-400 text-sm flex items-center gap-1 hover:text-brand-300">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-dark-700">
                  <th className="text-left pb-2">Name</th>
                  <th className="text-left pb-2">Role</th>
                  <th className="text-left pb-2">Location</th>
                  <th className="text-left pb-2">Skills</th>
                  <th className="text-right pb-2">TalentScore</th>
                </tr>
              </thead>
              <tbody>
                {topCandidates.map(c => (
                  <tr key={c.id} className="border-b border-dark-700 hover:bg-dark-700/30">
                    <td className="py-2.5">
                      <Link to={`/candidates/${c.id}`} className="text-gray-200 hover:text-brand-400 font-medium">{c.name}</Link>
                    </td>
                    <td className="py-2.5 text-gray-400">{c.current_role || '—'}</td>
                    <td className="py-2.5 text-gray-400">{c.location || '—'}</td>
                    <td className="py-2.5">
                      <div className="flex gap-1 flex-wrap">
                        {(c.skills || []).slice(0, 3).map(s => <span key={s} className="tag">{s}</span>)}
                      </div>
                    </td>
                    <td className="py-2.5 text-right">
                      <TalentScoreBadge score={c.talent_score} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
