import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { Plus, Search, MapPin, Briefcase, Calendar, Users, ChevronRight, X } from 'lucide-react'

const STATUS_COLORS = {
  OPEN: 'bg-green-500/10 text-green-400 border-green-500/30',
  PAUSED: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  CLOSED: 'bg-gray-500/10 text-gray-400 border-gray-500/30',
  DRAFT: 'bg-dark-600 text-gray-400 border-dark-500',
}
const SLA_COLORS = { green: 'text-green-400', amber: 'text-yellow-400', red: 'text-red-400' }

export default function Jobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', company: '', client_name: '', location: '', jd_text: '', salary_min: '', salary_max: '', experience_min: '', experience_max: '', domain: '' })
  const [creating, setCreating] = useState(false)
  const navigate = useNavigate()

  const load = () => api.jobs.list().then(setJobs).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      const payload = { ...form, salary_min: form.salary_min ? +form.salary_min : null, salary_max: form.salary_max ? +form.salary_max : null, experience_min: form.experience_min ? +form.experience_min : null, experience_max: form.experience_max ? +form.experience_max : null }
      const res = await api.jobs.create(payload)
      setShowForm(false)
      setForm({ title: '', company: '', client_name: '', location: '', jd_text: '', salary_min: '', salary_max: '', experience_min: '', experience_max: '', domain: '' })
      navigate(`/jobs/${res.id}`)
    } catch (err) { alert(err.message) }
    finally { setCreating(false) }
  }

  const filtered = jobs.filter(j => !search || j.title.toLowerCase().includes(search.toLowerCase()) || j.company.toLowerCase().includes(search.toLowerCase()) || (j.location || '').toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Job Requisitions</h1>
          <p className="text-gray-400 text-sm mt-1">{jobs.length} total jobs</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Job
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
        <input className="input w-full pl-9" placeholder="Search by title, company, location..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Jobs list */}
      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-16">
          <Briefcase size={40} className="mx-auto text-gray-600 mb-3" />
          <p className="text-gray-400">No jobs found. Create your first job requisition.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(job => (
            <Link key={job.id} to={`/jobs/${job.id}`} className="card block hover:border-brand-600/50 transition-colors group">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-white font-semibold text-lg group-hover:text-brand-400 transition-colors">{job.title}</h3>
                    <span className={`badge border ${STATUS_COLORS[job.status]}`}>{job.status}</span>
                    {job.sla_status !== 'green' && (
                      <span className={`text-xs font-medium ${SLA_COLORS[job.sla_status]}`}>
                        {job.sla_status === 'red' ? '⚠ SLA Breached' : '⚠ SLA Soon'}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span className="flex items-center gap-1"><Briefcase size={13} /> {job.company}{job.client_name ? ` · ${job.client_name}` : ''}</span>
                    {job.location && <span className="flex items-center gap-1"><MapPin size={13} /> {job.location}</span>}
                    {(job.experience_min || job.experience_max) && (
                      <span>{job.experience_min || 0}–{job.experience_max || '?'} yrs</span>
                    )}
                    {(job.salary_min || job.salary_max) && (
                      <span>₹{job.salary_min || 0}–{job.salary_max || '?'} LPA</span>
                    )}
                  </div>
                  {(job.skills_required || []).length > 0 && (
                    <div className="flex gap-1.5 mt-3 flex-wrap">
                      {job.skills_required.slice(0, 6).map(s => <span key={s} className="tag">{s}</span>)}
                      {job.skills_required.length > 6 && <span className="tag">+{job.skills_required.length - 6}</span>}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-6 ml-6 shrink-0">
                  <div className="text-center">
                    <div className="text-xl font-bold text-white">{job.active_candidates}</div>
                    <div className="text-xs text-gray-500">Active</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-white">{job.total_candidates}</div>
                    <div className="text-xs text-gray-500">Total</div>
                  </div>
                  <ChevronRight size={18} className="text-gray-600 group-hover:text-brand-400 transition-colors" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
          <div className="bg-dark-800 border border-dark-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-dark-700">
              <h2 className="text-lg font-bold text-white">Create New Job Requisition</h2>
              <button onClick={() => setShowForm(false)} className="text-gray-500 hover:text-gray-300"><X size={20} /></button>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-xs text-gray-400 mb-1 block">Job Title *</label><input className="input w-full" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="e.g. Senior React Developer" /></div>
                <div><label className="text-xs text-gray-400 mb-1 block">Company *</label><input className="input w-full" required value={form.company} onChange={e => setForm({...form, company: e.target.value})} placeholder="Hiring company" /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-xs text-gray-400 mb-1 block">Client Name</label><input className="input w-full" value={form.client_name} onChange={e => setForm({...form, client_name: e.target.value})} placeholder="Client org (if different)" /></div>
                <div><label className="text-xs text-gray-400 mb-1 block">Location</label><input className="input w-full" value={form.location} onChange={e => setForm({...form, location: e.target.value})} placeholder="Bangalore / Remote" /></div>
              </div>
              <div className="grid grid-cols-4 gap-4">
                <div><label className="text-xs text-gray-400 mb-1 block">Exp Min (yrs)</label><input type="number" className="input w-full" value={form.experience_min} onChange={e => setForm({...form, experience_min: e.target.value})} placeholder="3" /></div>
                <div><label className="text-xs text-gray-400 mb-1 block">Exp Max (yrs)</label><input type="number" className="input w-full" value={form.experience_max} onChange={e => setForm({...form, experience_max: e.target.value})} placeholder="7" /></div>
                <div><label className="text-xs text-gray-400 mb-1 block">Salary Min (LPA)</label><input type="number" className="input w-full" value={form.salary_min} onChange={e => setForm({...form, salary_min: e.target.value})} placeholder="12" /></div>
                <div><label className="text-xs text-gray-400 mb-1 block">Salary Max (LPA)</label><input type="number" className="input w-full" value={form.salary_max} onChange={e => setForm({...form, salary_max: e.target.value})} placeholder="20" /></div>
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Job Description — paste full JD for AI parsing</label>
                <textarea className="input w-full h-32 resize-none" value={form.jd_text} onChange={e => setForm({...form, jd_text: e.target.value})} placeholder="Paste the full job description here. AI will auto-extract skills, experience, domain, salary..." />
                {form.jd_text && <p className="text-xs text-brand-400 mt-1">✨ AI will auto-parse skills, experience, domain & salary</p>}
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={creating} className="btn-primary flex-1">{creating ? '⏳ Creating + Parsing JD...' : '🚀 Create Job'}</button>
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
