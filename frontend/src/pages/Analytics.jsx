import { useState, useEffect } from 'react'
import { api } from '../api/client'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  FunnelChart, Funnel, LabelList, LineChart, Line, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import TalentScoreBadge from '../components/TalentScoreBadge'
import { TrendingUp, Users, Briefcase, Target, Award, Clock } from 'lucide-react'

const COLORS = ['#6366f1', '#14b8a6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#10b981']

function StatCard({ icon: Icon, label, value, sub, color = 'brand' }) {
  const colorMap = {
    brand: 'text-brand-400',
    teal: 'text-teal-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  }
  return (
    <div className="card flex items-center gap-4">
      <div className={`${colorMap[color]} opacity-80`}><Icon size={28} /></div>
      <div>
        <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
        <div className="text-sm text-gray-400">{label}</div>
        {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
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
        <div key={i} style={{ color: p.color || '#a78bfa' }}>{p.name}: <span className="text-white font-bold">{p.value}</span></div>
      ))}
    </div>
  )
}

export default function Analytics() {
  const [stats, setStats] = useState(null)
  const [sourceData, setSourceData] = useState([])
  const [topCandidates, setTopCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.analytics.dashboard(),
      api.analytics.sourceEffectiveness(),
      api.analytics.topCandidates(10),
    ]).then(([s, src, top]) => {
      setStats(s)
      setSourceData(src)
      setTopCandidates(top)
    }).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" />
    </div>
  )

  const sourceChartData = (stats?.source_breakdown || []).map(s => ({
    name: s.source,
    candidates: s.count,
    avgScore: Math.round(s.avg_score || 0),
  }))

  const funnelData = (stats?.pipeline_funnel || [])
    .filter(f => f.count > 0)
    .map(f => ({ name: f.display_name, value: f.count, fill: COLORS[STAGE_COLORS[f.stage] || 0] }))

  const scoreDistribution = buildScoreDistribution(topCandidates)

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-2xl font-bold text-white">Analytics</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={Briefcase} label="Open Jobs" value={stats?.open_jobs} color="brand" />
        <StatCard icon={Users} label="Total Candidates" value={stats?.total_candidates} color="teal" />
        <StatCard icon={Award} label="Avg TalentScore" value={stats?.avg_talent_score ? Math.round(stats.avg_talent_score) : '—'} color="purple" />
        <StatCard icon={Target} label="Hired This Month" value={stats?.hired_this_month ?? 0} color="green" />
        <StatCard icon={Clock} label="SLA At Risk" value={stats?.sla_at_risk ?? 0} color="yellow" />
        <StatCard icon={TrendingUp} label="Interviews This Week" value={stats?.interviews_this_week ?? 0} color="teal" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Source Breakdown */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Candidates by Source</h3>
          {sourceChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceChartData} layout="vertical">
                <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={80} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="candidates" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-600 py-12">No source data yet</div>
          )}
        </div>

        {/* Avg Score by Source */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Avg TalentScore by Source</h3>
          {sourceChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={sourceChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="avgScore" fill="#14b8a6" radius={[4, 4, 0, 0]} name="Avg Score" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-600 py-12">No score data yet</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Pipeline Funnel */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Overall Pipeline Funnel</h3>
          {funnelData.length > 0 ? (
            <div className="space-y-1">
              {(stats?.pipeline_funnel || []).filter(f => f.count > 0).map((f, i, arr) => {
                const pct = arr[0]?.count > 0 ? Math.round((f.count / arr[0].count) * 100) : 0
                return (
                  <div key={f.stage}>
                    <div className="flex items-center justify-between text-sm mb-0.5">
                      <span className="text-gray-400">{f.display_name}</span>
                      <span className="text-white font-bold">{f.count} <span className="text-gray-500 text-xs font-normal">({pct}%)</span></span>
                    </div>
                    <div className="h-5 bg-dark-700 rounded overflow-hidden">
                      <div
                        className="h-full rounded transition-all"
                        style={{
                          width: `${pct}%`,
                          background: `hsl(${240 - (i * 20)}, 70%, 55%)`,
                        }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center text-gray-600 py-12">No pipeline data yet</div>
          )}
        </div>

        {/* Score Distribution */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">TalentScore Distribution</h3>
          {scoreDistribution.some(b => b.count > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={scoreDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="range" tick={{ fill: '#9ca3af', fontSize: 10 }} />
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
      </div>

      {/* Top Candidates Table */}
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
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Company</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Location</th>
                  <th className="text-left text-gray-500 font-medium pb-2 pr-4">Exp</th>
                  <th className="text-left text-gray-500 font-medium pb-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {topCandidates.map((c, i) => (
                  <tr key={c.id} className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors">
                    <td className="py-2 pr-4 text-gray-600 font-mono">{i + 1}</td>
                    <td className="py-2 pr-4">
                      <a href={`/candidates/${c.id}`} className="text-white hover:text-brand-400">{c.name}</a>
                    </td>
                    <td className="py-2 pr-4 text-gray-400">{c.current_role || '—'}</td>
                    <td className="py-2 pr-4 text-gray-400">{c.current_company || '—'}</td>
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
      {(stats?.recent_activity || []).length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-2">
            {stats.recent_activity.map((act, i) => (
              <div key={i} className="flex items-center gap-3 py-2 border-b border-dark-800 last:border-0">
                <div className="w-2 h-2 rounded-full bg-brand-500 shrink-0" />
                <div className="flex-1 text-sm text-gray-300">{act.message}</div>
                <div className="text-xs text-gray-600">{act.time_ago}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function buildScoreDistribution(candidates) {
  const buckets = [
    { range: '0-20', min: 0, max: 20, count: 0, color: '#ef4444' },
    { range: '20-40', min: 20, max: 40, count: 0, color: '#f97316' },
    { range: '40-60', min: 40, max: 60, count: 0, color: '#eab308' },
    { range: '60-80', min: 60, max: 80, count: 0, color: '#6366f1' },
    { range: '80-100', min: 80, max: 100, count: 0, color: '#22c55e' },
  ]
  for (const c of candidates) {
    const score = c.talent_score || 0
    const bucket = buckets.find(b => score >= b.min && score <= b.max)
    if (bucket) bucket.count++
  }
  return buckets
}

const STAGE_COLORS = {
  SOURCED: 0, APPROACHED: 1, RESPONDED: 2, SCREENING_SCHEDULED: 3,
  SCREENING_DONE: 4, SHORTLISTED: 5, L1_INTERVIEW: 6,
}
