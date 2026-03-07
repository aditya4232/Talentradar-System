import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import TalentScoreBadge from '../components/TalentScoreBadge'
import StageBadge from '../components/StageBadge'
import { Search, GitBranch, Mail, Plus, ChevronLeft, Loader } from 'lucide-react'

export default function JobDetail() {
  const { id } = useParams()
  const [job, setJob] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)
  const [tab, setTab] = useState('candidates')
  const [addingId, setAddingId] = useState(null)
  const [emailModal, setEmailModal] = useState(null)
  const [generatingEmail, setGeneratingEmail] = useState(false)
  const [emailData, setEmailData] = useState(null)
  const [sendingEmail, setSendingEmail] = useState(false)
  const [emailTone, setEmailTone] = useState('professional')

  useEffect(() => { api.jobs.get(+id).then(setJob).finally(() => setLoading(false)) }, [id])

  const searchCandidates = async () => {
    setSearching(true)
    try {
      const res = await api.candidates.searchForJob(+id, 50)
      setCandidates(res)
    } catch (e) { alert(e.message) }
    finally { setSearching(false) }
  }

  useEffect(() => { if (job) searchCandidates() }, [job])

  const addToPipeline = async (candidate) => {
    setAddingId(candidate.id)
    try {
      await api.pipeline.add({
        job_id: +id, candidate_id: candidate.id,
        talent_score: candidate.talent_score_for_job,
        score_breakdown: JSON.stringify(candidate.score_breakdown),
      })
      alert(`✅ ${candidate.name} added to pipeline!`)
    } catch (e) { alert(e.message) }
    finally { setAddingId(null) }
  }

  const openEmailModal = async (candidate) => {
    setEmailModal(candidate)
    setEmailData(null)
    setGeneratingEmail(true)
    try {
      const res = await api.outreach.generateEmail({ candidate_id: candidate.id, job_id: +id, tone: emailTone })
      setEmailData(res)
    } catch (e) { alert(e.message) }
    finally { setGeneratingEmail(false) }
  }

  const sendEmail = async () => {
    setSendingEmail(true)
    try {
      await api.outreach.send({ candidate_id: emailModal.id, job_id: +id, subject: emailData.subject, body: emailData.body })
      alert('✅ Email sent (or logged in dry-run mode)!')
      setEmailModal(null)
    } catch (e) { alert(e.message) }
    finally { setSendingEmail(false) }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
  if (!job) return <div className="text-gray-400 text-center py-20">Job not found</div>

  const parsed = job.parsed_requirements || {}

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <Link to="/jobs" className="text-gray-500 hover:text-gray-300 mt-1"><ChevronLeft size={20} /></Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white">{job.title}</h1>
          <p className="text-gray-400 text-sm">{job.company}{job.client_name ? ` · ${job.client_name}` : ''} · {job.location}</p>
        </div>
        <Link to={`/pipeline/${id}`} className="btn-primary flex items-center gap-2"><GitBranch size={15} /> Open Pipeline</Link>
      </div>

      {/* Job info */}
      <div className="grid grid-cols-4 gap-4">
        {[
          ['Experience', `${job.experience_min || 0}–${job.experience_max || '?'} yrs`],
          ['Salary', `₹${job.salary_min || 0}–${job.salary_max || '?'} LPA`],
          ['Domain', parsed.domain || job.domain || '—'],
          ['Seniority', parsed.seniority_level || '—'],
        ].map(([label, val]) => (
          <div key={label} className="card text-center">
            <div className="text-white font-semibold">{val}</div>
            <div className="text-xs text-gray-500 mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Skills */}
      {(job.skills_required || []).length > 0 && (
        <div className="card">
          <div className="text-sm font-medium text-gray-300 mb-3">Required Skills</div>
          <div className="flex flex-wrap gap-2">
            {job.skills_required.map(s => <span key={s} className="badge bg-brand-500/10 text-brand-300 border border-brand-500/20">{s}</span>)}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-dark-700">
        {[['candidates', `AI Matches (${candidates.length})`], ['jd', 'Job Description']].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${tab === key ? 'border-brand-500 text-brand-400' : 'border-transparent text-gray-500 hover:text-gray-300'}`}>{label}</button>
        ))}
      </div>

      {tab === 'jd' && (
        <div className="card">
          <pre className="text-sm text-gray-300 whitespace-pre-wrap">{job.jd_text || 'No JD text available.'}</pre>
        </div>
      )}

      {tab === 'candidates' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-400">Ranked by TalentScore for this role. Click + to add to pipeline, ✉ to send AI email.</p>
            <button onClick={searchCandidates} disabled={searching} className="btn-secondary flex items-center gap-2 text-sm">
              {searching ? <Loader size={14} className="animate-spin" /> : <Search size={14} />} Re-score
            </button>
          </div>
          {searching ? (
            <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
          ) : candidates.length === 0 ? (
            <div className="card text-center py-16 text-gray-500">No candidates found. Run a scraping job first.</div>
          ) : (
            <div className="space-y-2">
              {candidates.map((c, idx) => (
                <div key={c.id} className="card flex items-center gap-4 hover:border-brand-600/40 transition-colors">
                  <div className="text-gray-600 text-sm w-6 text-center shrink-0">#{idx + 1}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <Link to={`/candidates/${c.id}`} className="text-white font-semibold hover:text-brand-400">{c.name}</Link>
                      <TalentScoreBadge score={c.talent_score_for_job} size="sm" />
                    </div>
                    <div className="text-sm text-gray-400 mb-2">{c.current_role || '—'} · {c.current_company || '—'} · {c.location || '—'}</div>
                    {c.matched_skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {c.matched_skills.slice(0, 4).map(s => <span key={s} className="badge bg-green-500/10 text-green-300 border border-green-500/20">{s}</span>)}
                        {c.missing_skills?.slice(0, 2).map(s => <span key={s} className="badge bg-red-500/10 text-red-300 border border-red-500/20">−{s}</span>)}
                      </div>
                    )}
                    {c.score_explanation && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{c.score_explanation}</p>}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button onClick={() => openEmailModal(c)} title="Generate & send email" className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-400 hover:bg-teal-500/20 flex items-center justify-center transition-colors"><Mail size={14} /></button>
                    <button onClick={() => addToPipeline(c)} disabled={addingId === c.id} title="Add to pipeline" className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 hover:bg-brand-500/20 flex items-center justify-center transition-colors">
                      {addingId === c.id ? <Loader size={14} className="animate-spin" /> : <Plus size={14} />}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Email Modal */}
      {emailModal && (
        <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
          <div className="bg-dark-800 border border-dark-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-dark-700 flex justify-between">
              <h3 className="text-lg font-bold text-white">AI Outreach Email — {emailModal.name}</h3>
              <button onClick={() => setEmailModal(null)} className="text-gray-500 hover:text-gray-300">✕</button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex gap-2">
                {['professional', 'casual', 'startup', 'corporate'].map(t => (
                  <button key={t} onClick={() => { setEmailTone(t); openEmailModal(emailModal) }}
                    className={`px-3 py-1 rounded-lg text-sm capitalize transition-colors ${emailTone === t ? 'bg-brand-600 text-white' : 'bg-dark-700 text-gray-400 hover:text-gray-200'}`}>{t}</button>
                ))}
              </div>
              {generatingEmail ? (
                <div className="flex items-center gap-2 text-gray-400"><Loader size={16} className="animate-spin" /> Generating AI email...</div>
              ) : emailData && (
                <>
                  <div><label className="text-xs text-gray-500 mb-1 block">Subject</label><input className="input w-full" value={emailData.subject} onChange={e => setEmailData({...emailData, subject: e.target.value})} /></div>
                  <div><label className="text-xs text-gray-500 mb-1 block">Body</label><textarea className="input w-full h-48 resize-none" value={emailData.body} onChange={e => setEmailData({...emailData, body: e.target.value})} /></div>
                </>
              )}
              <div className="flex gap-3">
                <button onClick={sendEmail} disabled={!emailData || sendingEmail} className="btn-primary flex-1">{sendingEmail ? '⏳ Sending...' : '✉ Send Email'}</button>
                <button onClick={() => setEmailModal(null)} className="btn-secondary">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
