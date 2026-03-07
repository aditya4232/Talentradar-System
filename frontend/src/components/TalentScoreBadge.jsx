export default function TalentScoreBadge({ score, size = 'md', showLabel = true }) {
  const s = score || 0
  const color = s >= 80 ? 'text-green-400 bg-green-400/10 border-green-400/30'
              : s >= 60 ? 'text-brand-400 bg-brand-400/10 border-brand-400/30'
              : s >= 40 ? 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'
              : 'text-red-400 bg-red-400/10 border-red-400/30'

  const sizes = { sm: 'text-xs px-2 py-0.5', md: 'text-sm px-3 py-1', lg: 'text-base px-4 py-1.5' }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-bold ${color} ${sizes[size]}`}>
      <span>{s.toFixed(0)}</span>
      {showLabel && <span className="font-normal opacity-70">/ 100</span>}
    </span>
  )
}
