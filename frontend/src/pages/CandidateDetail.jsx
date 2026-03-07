import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import TalentScoreBadge from '../components/TalentScoreBadge'
import StageBadge from '../components/StageBadge'
import { ChevronLeft, Github, Linkedin, Mail, Phone, MapPin, Building, Clock, GraduationCap } from 'lucide-react'

export default function CandidateDetail() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [pipelines, setPipelines] = useState([])
  const [outreach, setOutreach] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.candidates.get(+id),
      api.pipeline.candidatePipelines(+id),
      api.outreach.history(+id),
    ]).then(([c, p, o]) => { setCandidate(c); setPipelines(p); setOutreach(o) })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
  if (!candidate) return <div className="text-gray-400 text-center py-20">Candidate not found</div>

  const c = candidate
  const lastActive = c.last_active ? new Date(c.last_active) : null
  const daysAgo = lastActive ? Math.floor((Date.now() - lastActive) / 86400000) : null

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-3">
        <Link to="/candidates" className="text-gray-500 hover:text-gray-300"><ChevronLeft size={20} /></Link>
        <h1 className="text-2xl font-bold text-white">{c.name}</h1>
      </div>

      {/* Header Card */}
      <div className="card">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-600 to-teal-500 flex items-center justify-center text-white text-2xl font-bold shrink-0">{c.name[0]}</div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-xl font-bold text-white">{c.name}</h2>
              <TalentScoreBadge score={c.talent_score} />
            </div>
            <div className="text-gray-400 mb-3">{c.current_role || '—'} @ {c.current_company || '—'}</div>
            <div className="flex flex-wrap gap-4 text-sm text-gray-400">
              {c.location && <span className="flex items-center gap-1.5"><MapPin size={14} />{c.location}</span>}
              {c.experience_years && <span className="flex items-center gap-1.5"><Clock size={14} />{c.experience_years} yrs exp</span>}
              {c.email && <span className="flex items-center gap-1.5"><Mail size={14} />{c.email}</span>}
              {c.phone && <span className="flex items-center gap-1.5"><Phone size={14} />{c.phone}</span>}
              {daysAgo !== null && <span className="flex items-center gap-1.5 text-green-400">● Active {daysAgo === 0 ? 'today' : `${daysAgo}d ago`}</span>}
            </div>
            <div className="flex gap-3 mt-3">
              {c.github_url && <a href={c.github_url} target="_blank" rel="noopener" className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm"><Github size={14} /> GitHub</a>}
              {c.linkedin_url && <a href={c.linkedin_url} target="_blank" rel="noopener" className="flex items-center gap-1.5 text-gray-400 hover:text-blue-400 text-sm"><Linkedin size={14} /> LinkedIn</a>}
              {c.naukri_url && <a href={c.naukri_url} target="_blank" rel="noopener" className="flex items-center gap-1.5 text-gray-400 hover:text-yellow-400 text-sm">📋 Naukri</a>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 shrink-0">
            {c.salary_current && <div className="card bg-dark-700 text-center py-2 px-3"><div className="text-white font-bold">₹{c.salary_current}L</div><div className="text-xs text-gray-500">Current CTC</div></div>}
            {c.salary_expected && <div className="card bg-dark-700 text-center py-2 px-3"><div className="text-white font-bold">₹{c.salary_expected}L</div><div className="text-xs text-gray-500">Expected</div></div>}
            {c.notice_period != null && <div className="card bg-dark-700 text-center py-2 px-3"><div className="text-white font-bold">{c.notice_period}d</div><div className="text-xs text-gray-500">Notice</div></div>}
            {c.freshness_score && <div className="card bg-dark-700 text-center py-2 px-3"><div className="text-white font-bold">{Math.round(c.freshness_score * 100)}%</div><div className="text-xs text-gray-500">Freshness</div></div>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Skills */}
        <div className="card">
          <h3 className="font-semibold text-white mb-3">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {(c.skills || []).map(s => <span key={s} className="badge bg-brand-500/10 text-brand-300 border border-brand-500/20">{s}</span>)}
            {(c.skills || []).length === 0 && <span className="text-gray-500 text-sm">No skills listed</span>}
          </div>
        </div>

        {/* Summary */}
        <div className="card">
          <h3 className="font-semibold text-white mb-3">AI Summary</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{c.summary || 'No summary available.'}</p>
        </div>
      </div>

      {/* Work History */}
      {(c.work_history || []).length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Work History</h3>
          <div className="space-y-3">
            {c.work_history.map((w, i) => (
              <div key={i} className="flex items-start gap-3 border-b border-dark-700 pb-3 last:border-0">
                <div className="w-8 h-8 rounded-lg bg-dark-700 flex items-center justify-center shrink-0"><Building size={14} className="text-gray-400" /></div>
                <div>
                  <div className="text-white font-medium">{w.role || '—'}</div>
                  <div className="text-gray-400 text-sm">{w.company || '—'} · {w.duration || '—'}</div>
                  {w.description && <div className="text-gray-500 text-xs mt-1">{w.description}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {(c.education || []).length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Education</h3>
          <div className="space-y-2">
            {c.education.map((e, i) => (
              <div key={i} className="flex items-center gap-3">
                <GraduationCap size={16} className="text-gray-400 shrink-0" />
                <div>
                  <div className="text-white text-sm font-medium">{e.degree || '—'}</div>
                  <div className="text-gray-500 text-xs">{e.institution || '—'} · {e.year || '—'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Jobs */}
      {pipelines.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Active Job Pipelines</h3>
          <div className="space-y-2">
            {pipelines.map(p => (
              <div key={p.entry_id} className="flex items-center justify-between py-2 border-b border-dark-700 last:border-0">
                <div>
                  <Link to={`/pipeline/${p.job_id}`} className="text-white hover:text-brand-400 text-sm font-medium">{p.job_title}</Link>
                  <div className="text-xs text-gray-500">{p.company}</div>
                </div>
                <div className="flex items-center gap-3">
                  {p.talent_score && <TalentScoreBadge score={p.talent_score} size="sm" />}
                  <StageBadge stage={p.stage} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Outreach history */}
      {outreach.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Outreach History</h3>
          <div className="space-y-2">
            {outreach.map(o => (
              <div key={o.id} className="flex items-start gap-3 py-2 border-b border-dark-700 last:border-0">
                <span className="text-xs text-gray-500 uppercase badge bg-dark-700">{o.channel}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-300 truncate">{o.subject || 'No subject'}</div>
                  <div className="text-xs text-gray-600">{o.sent_at ? new Date(o.sent_at).toLocaleDateString() : '—'} · {o.status}</div>
                </div>
                <div className="flex gap-2 text-xs">
                  {o.opened_at && <span className="text-green-400">Opened</span>}
                  {o.replied_at && <span className="text-brand-400">Replied</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
