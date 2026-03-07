const STAGE_COLORS = {
  SOURCED: 'bg-gray-600/20 text-gray-300 border-gray-600/30',
  APPROACHED: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
  RESPONDED: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
  SCREENING_SCHEDULED: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
  SCREENING_DONE: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
  SHORTLISTED: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  L1_INTERVIEW: 'bg-yellow-500/10 text-yellow-300 border-yellow-500/30',
  L2_INTERVIEW: 'bg-orange-500/10 text-orange-300 border-orange-500/30',
  OFFER_SENT: 'bg-pink-500/10 text-pink-300 border-pink-500/30',
  OFFER_ACCEPTED: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  JOINED: 'bg-green-500/10 text-green-300 border-green-500/30',
  REJECTED: 'bg-red-500/10 text-red-300 border-red-500/30',
  ON_HOLD: 'bg-gray-500/10 text-gray-400 border-gray-500/30',
}

const STAGE_LABELS = {
  SOURCED: 'Sourced', APPROACHED: 'Approached', RESPONDED: 'Responded',
  SCREENING_SCHEDULED: 'Screening', SCREENING_DONE: 'Screened',
  SHORTLISTED: 'Shortlisted', L1_INTERVIEW: 'L1', L2_INTERVIEW: 'L2',
  OFFER_SENT: 'Offer Sent', OFFER_ACCEPTED: 'Accepted', JOINED: 'Joined',
  REJECTED: 'Rejected', ON_HOLD: 'On Hold',
}

export default function StageBadge({ stage }) {
  return (
    <span className={`badge border ${STAGE_COLORS[stage] || 'bg-gray-700 text-gray-300 border-gray-600'}`}>
      {STAGE_LABELS[stage] || stage}
    </span>
  )
}
