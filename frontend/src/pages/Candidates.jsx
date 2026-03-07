import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import TalentScoreBadge from '../components/TalentScoreBadge'
import { Search, Filter, Users, MapPin, Briefcase, Github, Linkedin } from 'lucide-react'

export default function Candidates() {
  const [candidates, setCandidates] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [expMin, setExpMin] = useState('')
  const [expMax, setExpMax] = useState('')
  const [page, setPage] = useState(1)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [res, countRes] = await Promise.all([
        api.candidates.list({ q: search || undefined, location: location || undefined, exp_min: expMin || undefined, exp_max: expMax || undefined, page, limit: 50 }),
        api.candidates.count(),
      ])
      setCandidates(res)
      setTotal(countRes.total)
    } finally { setLoading(false) }
  }, [search, location, expMin, expMax, page])

  useEffect(() => {
    const timer = setTimeout(load, 300)
    return () => clearTimeout(timer)
  }, [load])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Candidates</h1>
          <p className="text-gray-400 text-sm mt-1">{total.toLocaleString()} total candidates in database</p>
        </div>
        <Link to="/scrape" className="btn-primary flex items-center gap-2"><Search size={15} /> Source Candidates</Link>
      </div>

      {/* Filters */}
      <div className="card flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input className="input w-full pl-9 text-sm" placeholder="Name, role, skills, company..." value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} />
        </div>
        <input className="input text-sm w-36" placeholder="Location" value={location} onChange={e => { setLocation(e.target.value); setPage(1) }} />
        <input type="number" className="input text-sm w-24" placeholder="Exp min" value={expMin} onChange={e => { setExpMin(e.target.value); setPage(1) }} />
        <input type="number" className="input text-sm w-24" placeholder="Exp max" value={expMax} onChange={e => { setExpMax(e.target.value); setPage(1) }} />
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
      ) : candidates.length === 0 ? (
        <div className="card text-center py-20">
          <Users size={40} className="mx-auto text-gray-600 mb-3" />
          <p className="text-gray-400 mb-4">No candidates found. Source candidates to get started.</p>
          <Link to="/scrape" className="btn-primary inline-flex items-center gap-2"><Search size={14} /> Go to Source</Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
            {candidates.map(c => (
              <Link key={c.id} to={`/candidates/${c.id}`} className="card hover:border-brand-600/50 transition-colors group block">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-600 to-teal-500 flex items-center justify-center text-white font-bold shrink-0">
                    {c.name[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-semibold group-hover:text-brand-400 transition-colors truncate">{c.name}</span>
                      <TalentScoreBadge score={c.talent_score} size="sm" />
                    </div>
                    <div className="text-sm text-gray-400 truncate mb-2">
                      <span>{c.current_role || '—'}</span>
                      {c.current_company && <span className="text-gray-500"> @ {c.current_company}</span>}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mb-2">
                      {c.location && <span className="flex items-center gap-1"><MapPin size={11} />{c.location}</span>}
                      {c.experience_years && <span>{c.experience_years} yrs exp</span>}
                      {c.salary_expected && <span>₹{c.salary_expected}L expected</span>}
                      {c.notice_period != null && <span>{c.notice_period}d notice</span>}
                    </div>
                    <div className="flex gap-1 flex-wrap">
                      {(c.skills || []).slice(0, 5).map(s => <span key={s} className="tag">{s}</span>)}
                      {(c.skills || []).length > 5 && <span className="tag">+{c.skills.length - 5}</span>}
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 items-end shrink-0">
                    {c.github_url && <a href={c.github_url} target="_blank" rel="noopener" onClick={e => e.stopPropagation()} className="text-gray-500 hover:text-white"><Github size={14} /></a>}
                    {c.linkedin_url && <a href={c.linkedin_url} target="_blank" rel="noopener" onClick={e => e.stopPropagation()} className="text-gray-500 hover:text-blue-400"><Linkedin size={14} /></a>}
                    <div className="flex gap-1 flex-wrap justify-end">
                      {(c.sources || []).slice(0, 2).map(src => <span key={src} className="tag capitalize text-xs">{src}</span>)}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {candidates.length >= 50 && (
            <div className="flex justify-center gap-3">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary">← Prev</button>
              <span className="text-gray-400 text-sm flex items-center">Page {page}</span>
              <button onClick={() => setPage(p => p + 1)} className="btn-secondary">Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
