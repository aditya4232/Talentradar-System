import { useState, useEffect } from 'react'
import { api } from '../api/client'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Cell,
} from 'recharts'
import TalentScoreBadge from '../components/TalentScoreBadge'
import { TrendingUp, Users, Briefcase, Target, Award, Clock } from 'lucide-react'

const STAGE_DISPLAY = {
  SOURCED: 'Sourced', APPROACHED: 'Approached', RESPONDED: 'Responded',
  SCREENING_SCHEDULED: 'Screening Sched.', SCREENING_DONE: 'Screening Done',
  SHORTLISTED: 'Shortlisted', L1_INTERVIEW: 'L1 Interview', L2_INTERVIEW: 'L2 Interview',
  OFFER_SENT: 'Offer Sent', OFFER_ACCEPTED: 'Offer Accepted', JOINED: 'Joined',
}

function StatCard({ icon: Icon, label, value, color = 'brand' }) {
  const colorMap = {
    brand: 'text-brand-400', teal: 'text-teal-400', green: 'text-green-400',
    yellow: 'text-yellow-400', red: 'text-red-400', purple: 'text-purple-400',
  }
  return (
    <div className="card flex items-center gap-4">
      <div className={`${colorMap[color]} opacity-80`}><Icon size={26} /></div>
      <div>
        <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
        <div className="text-sm text-gray-400">{label}</div>
      </div>
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm shadow-xl">
      <div className="text-gray-400 mb-1">{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || '#a78bfa' }}>
          {p.name}: <span className="text-white font-bold">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

function buildScoreDistribution(candidates) {
  const buckets = [
    { range: '0-20', min: 0, max: 20, count: 0, color: '#ef4444' },
    { range: '20-40', min: 20, max: 40, count: 0, color: '#f97316' },
    { range: '40-60', min: 40, max: 60, count: 0, color: '#eab308' },
    { range: '60-80', min: 60, max: 80, count: 0, color: '#6366f1' },
    { range: '80-100', min: 80, max: 101, count: 0, color: '#22c55e' },
  ]
  for (const c of candidates) {
    const score = c.talent_score || 0
    const bucket = buckets.find(b => score >= b.min && score < b.max)
    if (bucket) bucket.count++
  }
  return buckets
}

export default function Analytics() {
  const [dashboard, setDashboard] = useState(null)
  const [sourceEff, setSourceEff] = useState([])
  const [topCandidates, setTopCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.analytics.dashboard(),
      api.analytics.sourceEffectiveness(),
      api.analytics.topCandidates(10),
    ]).then(([d, src, top]) => {
      setDashboard(d)
      setSourceEff(src)
      setTopCandidates(top)
    }).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" />
    </div>
  )

  // dashboard shape: { stats: {...}, source_breakdown: {"github": 50, ...}, recent_activity: [...] }
  const s = dashboard?.stats || {}
  const sourceBreakdown = dashboard?.source_breakdown || {}
  const recentActivity = dashboard?.recent_activity || []

  // Convert source_breakdown dict to chart array
  const sourceChartData = Object.entries(sourceBreakdown)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)

  // Source effectiveness from /analytics/source-effectiveness
  // shape: [{ source, candidates, avg_score, hires, hire_rate }]
  const sourceEffChart = sourceEff.map(s => ({
    name: s.source,
    avgScore: Math.round(s.avg_score || 0),
    candidates: s.candidates,
    hires: s.hires,
  }))

  const scoreDistribution = buildScoreDistribution(topCandidates)

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-2xl font-bold text-white">Analytics</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={Briefcase} label="Open Jobs" value={s.open_jobs} color="brand" />
        <StatCard icon={Users} label="Total Candidates" value={s.total_candidates} color="teal" />
        <StatCard icon={Award} label="Avg TalentScore" value={s.avg_talent_score ? Math.round(s.avg_talent_score) : '—'} color="purple" />
        <StatCard icon={Target} label="Placements" value={s.placements ?? 0} color="green" />
        <StatCard icon={Clock} label="SLA At Risk" value={s.sla_at_risk ?? 0} color="yellow" />
        <StatCard icon={TrendingUp} label="Interviews" value={s.interviews_scheduled ?? 0} color="teal" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Source Breakdown */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Candidates by Source</h3>
          {sourceChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceChartData} layout="vertical">
                <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={70} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} name="Candidates" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-600 py-12">No candidates sourced yet. Seed demo data to start.</div>
          )}
        </div>

        {/* Avg Score by Source */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Avg TalentScore by Source</h3>
          {sourceEffChart.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceEffChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="avgScore" fill="#14b8a6" radius={[4, 4, 0, 0]} name="Avg Score" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-600 py-12">No source data yet</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Score Distribution */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">TalentScore Distribution (Top 10)</h3>
          {scoreDistribution.some(b => b.count > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={scoreDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="range" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Candidates" radius={[4, 4, 0, 0]}>
                  {scoreDistribution.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-600 py-12">No candidates scored yet</div>
          )}
        </div>

        {/* Source Hire Rate */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Source Effectiveness</h3>
          {sourceEff.length > 0 ? (
            <div className="space-y-3">
              {sourceEff.slice(0, 6).map(s => (
                <div key={s.source}>
                  <div className="flex justify-between text-sm mb-0.5">
                    <span className="text-gray-400 capitalize">{s.source}</span>
                    <span className="text-white font-medium">
                      {s.candidates} cands · {s.hires} hired
                      <span className="text-gray-500 ml-1 text-xs">({s.hire_rate}%)</span>
                    </span>
                  </div>
                  <div className="h-2 bg-dark-700 rounded overflow-hidden">
                    <div
                      className="h-full rounded"
                      style={{
                        width: `${Math.min(s.avg_score, 100)}%`,
                        background: s.avg_score >= 70 ? '#22c55e' : s.avg_score >= 50 ? '#6366f1' : '#eab308',
                      }}
                    />
                  </div>
                  <div className="text-xs text-gray-600 mt-0.5">Avg score: {s.avg_score}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-600 py-12">No source data yet</div>
          )}
        </div>
      </div>

      {/* Top Candidates */}
      {topCandidates.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Top Candidates by TalentScore</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">#</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Name</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Role</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Location</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Exp</th>
                  <th className="text-left text-gray-500 font-medium pb-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {topCandidates.map((c, i) => (
                  <tr key={c.id} className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors">
                    <td className="py-2 pr-4 text-gray-600 font-mono text-xs">{i + 1}</td>
                    <td className="py-2 pr-4">
                      <a href={`/candidates/${c.id}`} className="text-white hover:text-brand-400">{c.name}</a>
                    </td>
                    <td className="py-2 pr-4 text-gray-400">{c.current_role || '—'}</td>
                    <td className="py-2 pr-4 text-gray-500">{c.location || '—'}</td>
                    <td className="py-2 pr-4 text-gray-400">{c.experience_years ? `${c.experience_years}y` : '—'}</td>
                    <td className="py-2"><TalentScoreBadge score={c.talent_score} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {recentActivity.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Recent Pipeline Activity</h3>
          <div className="space-y-2">
            {recentActivity.map((act, i) => (
              <div key={i} className="flex items-center gap-3 py-2 border-b border-dark-800 last:border-0">
                <div className="w-2 h-2 rounded-full bg-brand-500 shrink-0" />
                <div className="flex-1 text-sm text-gray-300">
                  <span className="text-white font-medium">{act.candidate}</span>
                  {' → '}
                  <span className="text-brand-400">{STAGE_DISPLAY[act.stage] || act.stage}</span>
                  {' for '}
                  <span className="text-gray-400">{act.job}</span>
                  <span className="text-gray-600"> @ {act.company}</span>
                </div>
                <div className="text-xs text-gray-600 shrink-0">
                  {act.time ? new Date(act.time).toLocaleDateString() : '—'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
