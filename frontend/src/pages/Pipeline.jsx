import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import TalentScoreBadge from '../components/TalentScoreBadge'
import StageBadge from '../components/StageBadge'
import { ChevronLeft, GripVertical, ArrowRight, Trash2, FileText, X, Check } from 'lucide-react'

const STAGE_ORDER = [
  'SOURCED', 'APPROACHED', 'RESPONDED', 'SCREENING_SCHEDULED',
  'SCREENING_DONE', 'SHORTLISTED', 'L1_INTERVIEW', 'L2_INTERVIEW',
  'OFFER_SENT', 'OFFER_ACCEPTED', 'JOINED',
]

const TERMINAL_STAGES = ['REJECTED', 'ON_HOLD']
const ALL_STAGES = [...STAGE_ORDER, ...TERMINAL_STAGES]

const STAGE_DISPLAY = {
  SOURCED: 'Sourced',
  APPROACHED: 'Approached',
  RESPONDED: 'Responded',
  SCREENING_SCHEDULED: 'Screening Scheduled',
  SCREENING_DONE: 'Screening Done',
  SHORTLISTED: 'Shortlisted',
  L1_INTERVIEW: 'L1 Interview',
  L2_INTERVIEW: 'L2 Interview',
  OFFER_SENT: 'Offer Sent',
  OFFER_ACCEPTED: 'Offer Accepted',
  JOINED: 'Joined',
  REJECTED: 'Rejected',
  ON_HOLD: 'On Hold',
}

const STAGE_COLORS = {
  SOURCED: 'border-gray-600',
  APPROACHED: 'border-blue-600',
  RESPONDED: 'border-cyan-600',
  SCREENING_SCHEDULED: 'border-indigo-600',
  SCREENING_DONE: 'border-purple-600',
  SHORTLISTED: 'border-brand-600',
  L1_INTERVIEW: 'border-orange-600',
  L2_INTERVIEW: 'border-orange-500',
  OFFER_SENT: 'border-yellow-500',
  OFFER_ACCEPTED: 'border-green-600',
  JOINED: 'border-green-400',
  REJECTED: 'border-red-700',
  ON_HOLD: 'border-gray-500',
}

function NotesModal({ entry, onClose, onSave }) {
  const [notes, setNotes] = useState(entry.notes || '')
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    setSaving(true)
    try {
      await api.pipeline.updateNotes(entry.entry_id, notes)
      onSave(entry.entry_id, notes)
      onClose()
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="card w-full max-w-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-white">Notes — {entry.candidate_name}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X size={18} /></button>
        </div>
        <textarea
          className="input w-full h-40 resize-none"
          placeholder="Add interview notes, feedback, observations..."
          value={notes}
          onChange={e => setNotes(e.target.value)}
        />
        <div className="flex gap-2 mt-3 justify-end">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? 'Saving…' : 'Save Notes'}
          </button>
        </div>
      </div>
    </div>
  )
}

function CandidateCard({ entry, onMove, onDelete, onNotesClick }) {
  const [showMoveMenu, setShowMoveMenu] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    function handler(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setShowMoveMenu(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const nextStages = ALL_STAGES.filter(s => s !== entry.stage)

  return (
    <div className={`bg-dark-800 border border-dark-700 rounded-xl p-3 hover:border-dark-500 transition-colors`}>
      <div className="flex items-start justify-between mb-2">
        <Link to={`/candidates/${entry.candidate_id}`} className="text-white font-medium text-sm hover:text-brand-400 truncate pr-2">
          {entry.candidate_name}
        </Link>
        <div className="flex items-center gap-1 shrink-0">
          <button onClick={() => onNotesClick(entry)} className="text-gray-500 hover:text-gray-300 p-0.5 rounded" title="Notes">
            <FileText size={13} />
          </button>
          <button onClick={() => onDelete(entry.entry_id)} className="text-gray-500 hover:text-red-400 p-0.5 rounded" title="Remove">
            <Trash2 size={13} />
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-500 mb-2 truncate">{entry.current_role || '—'} @ {entry.current_company || '—'}</div>

      <div className="flex items-center justify-between">
        {entry.talent_score_for_job
          ? <TalentScoreBadge score={entry.talent_score_for_job} size="sm" />
          : <span className="text-xs text-gray-600">No score</span>
        }
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowMoveMenu(v => !v)}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-brand-400 px-1.5 py-0.5 rounded hover:bg-dark-700"
          >
            Move <ArrowRight size={10} />
          </button>
          {showMoveMenu && (
            <div className="absolute right-0 top-6 bg-dark-700 border border-dark-600 rounded-lg shadow-xl z-20 w-48 py-1 max-h-64 overflow-y-auto">
              {nextStages.map(s => (
                <button
                  key={s}
                  onClick={() => { onMove(entry.entry_id, s); setShowMoveMenu(false) }}
                  className="w-full text-left px-3 py-1.5 text-xs text-gray-300 hover:bg-dark-600 hover:text-white"
                >
                  → {STAGE_DISPLAY[s]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {entry.notes && (
        <div className="mt-2 text-xs text-gray-500 italic truncate border-t border-dark-700 pt-1.5">
          {entry.notes}
        </div>
      )}
    </div>
  )
}

function StageColumn({ stage, entries, onMove, onDelete, onNotesClick }) {
  return (
    <div className={`flex-shrink-0 w-64 bg-dark-900 border-t-2 ${STAGE_COLORS[stage]} rounded-xl flex flex-col max-h-full`}>
      <div className="px-3 py-2.5 border-b border-dark-700">
        <div className="flex items-center justify-between">
          <span className="text-white text-sm font-semibold">{STAGE_DISPLAY[stage]}</span>
          <span className="text-xs bg-dark-700 text-gray-400 rounded-full px-2 py-0.5">{entries.length}</span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-2 min-h-16">
        {entries.map(entry => (
          <CandidateCard
            key={entry.entry_id}
            entry={entry}
            onMove={onMove}
            onDelete={onDelete}
            onNotesClick={onNotesClick}
          />
        ))}
        {entries.length === 0 && (
          <div className="text-center text-gray-700 text-xs py-4">Empty</div>
        )}
      </div>
    </div>
  )
}

export default function Pipeline() {
  const { jobId } = useParams()
  const [board, setBoard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notesEntry, setNotesEntry] = useState(null)
  const [activeStages, setActiveStages] = useState(STAGE_ORDER)
  const [showTerminal, setShowTerminal] = useState(false)

  async function loadBoard() {
    try {
      const data = await api.pipeline.board(+jobId)
      setBoard(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadBoard() }, [jobId])

  async function handleMove(entryId, newStage) {
    await api.pipeline.move(entryId, newStage)
    await loadBoard()
  }

  async function handleDelete(entryId) {
    if (!confirm('Remove this candidate from the pipeline?')) return
    await api.pipeline.remove(entryId)
    await loadBoard()
  }

  function handleNotesSave(entryId, notes) {
    setBoard(prev => ({
      ...prev,
      stages: Object.fromEntries(
        Object.entries(prev.stages).map(([stage, entries]) => [
          stage,
          entries.map(e => e.entry_id === entryId ? { ...e, notes } : e)
        ])
      )
    }))
  }

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" /></div>
  if (!board) return <div className="text-gray-400 text-center py-20">Pipeline not found</div>

  const visibleStages = showTerminal ? [...activeStages, ...TERMINAL_STAGES] : activeStages

  const totalActive = STAGE_ORDER.reduce((sum, s) => sum + (board.stages[s]?.length || 0), 0)
  const rejected = (board.stages['REJECTED'] || []).length
  const onHold = (board.stages['ON_HOLD'] || []).length

  return (
    <div className="flex flex-col h-full -m-6">
      {/* Header */}
      <div className="px-6 py-4 border-b border-dark-700 flex items-center gap-4 shrink-0">
        <Link to={`/jobs/${jobId}`} className="text-gray-500 hover:text-gray-300"><ChevronLeft size={20} /></Link>
        <div>
          <h1 className="text-xl font-bold text-white">{board.job?.title}</h1>
          <div className="text-sm text-gray-500">{board.job?.company} · Pipeline Board</div>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex gap-3 text-sm">
            <span className="text-gray-400">{totalActive} active</span>
            {rejected > 0 && <span className="text-red-400">{rejected} rejected</span>}
            {onHold > 0 && <span className="text-yellow-400">{onHold} on hold</span>}
          </div>
          <button
            onClick={() => setShowTerminal(v => !v)}
            className={`btn-secondary text-xs py-1 px-3 ${showTerminal ? 'bg-dark-600' : ''}`}
          >
            {showTerminal ? 'Hide' : 'Show'} Rejected/Hold
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto p-6">
        <div className="flex gap-4 h-full min-w-max">
          {visibleStages.map(stage => (
            <StageColumn
              key={stage}
              stage={stage}
              entries={board.stages[stage] || []}
              onMove={handleMove}
              onDelete={handleDelete}
              onNotesClick={setNotesEntry}
            />
          ))}
        </div>
      </div>

      {/* Funnel Summary */}
      {board.funnel && (
        <div className="px-6 py-3 border-t border-dark-700 shrink-0">
          <div className="flex items-center gap-1 overflow-x-auto">
            {board.funnel.filter(f => f.count > 0).map((f, i, arr) => (
              <div key={f.stage} className="flex items-center gap-1 shrink-0">
                <div className="text-center">
                  <div className="text-white text-sm font-bold">{f.count}</div>
                  <div className="text-gray-500 text-xs">{f.display_name.split(' ')[0]}</div>
                </div>
                {i < arr.length - 1 && <span className="text-gray-700 mx-1">→</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {notesEntry && (
        <NotesModal
          entry={notesEntry}
          onClose={() => setNotesEntry(null)}
          onSave={handleNotesSave}
        />
      )}
    </div>
  )
}
