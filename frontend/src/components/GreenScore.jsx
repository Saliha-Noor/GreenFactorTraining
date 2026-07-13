import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'

function ScoreRing({ score, size = 140 }) {
  const pct     = score / 100
  const radius  = 54
  const circ    = 2 * Math.PI * radius
  const dash    = pct * circ
  const color   = score >= 75 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <svg width={size} height={size} viewBox="0 0 140 140">
      <circle cx="70" cy="70" r={radius} fill="none" stroke="#1e331e" strokeWidth="10" />
      <circle
        cx="70" cy="70" r={radius}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        transform="rotate(-90 70 70)"
        style={{ transition: 'stroke-dasharray 1s ease, stroke 0.5s' }}
        filter={`drop-shadow(0 0 8px ${color}88)`}
      />
      <text x="70" y="68" textAnchor="middle" fill={color}
        style={{ fontFamily: "'Syne',sans-serif", fontSize: 30, fontWeight: 800 }}>
        {score}
      </text>
      <text x="70" y="88" textAnchor="middle" fill="#567056"
        style={{ fontFamily: "'Inter',sans-serif", fontSize: 11 }}>
        / 100
      </text>
    </svg>
  )
}

function SubScore({ label, value }) {
  const color = value >= 75 ? 'var(--green-500)' : value >= 50 ? 'var(--amber-500)' : 'var(--red-500)'
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color, fontWeight: 600 }}>
          {value}
        </span>
      </div>
      <div style={{ height: 5, borderRadius: 99, background: 'var(--bg-surface)', overflow: 'hidden' }}>
        <div style={{
          height:     '100%',
          width:      `${value}%`,
          background: color,
          borderRadius: 99,
          transition: 'width 1s ease',
          boxShadow:  `0 0 8px ${color}66`,
        }} />
      </div>
    </div>
  )
}

export default function GreenScore({ data }) {
  const { overall, performance, energy, carbon, maintainability } = data

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <p className="section-label" style={{ marginBottom: 20 }}>Green Score</p>

      <div style={{ display: 'flex', gap: 32, alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Ring */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          <ScoreRing score={overall} />
          <span style={{
            fontFamily: 'var(--font-display)',
            fontSize:   '0.85rem',
            fontWeight: 700,
            color:      overall >= 75 ? 'var(--green-400)' :
                        overall >= 50 ? 'var(--amber-400)' : 'var(--red-500)',
          }}>
            {overall >= 75 ? 'Excellent' : overall >= 50 ? 'Needs Work' : 'Poor'}
          </span>
        </div>

        {/* Sub-scores */}
        <div style={{ flex: 1, minWidth: 200, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <SubScore label="Performance"     value={performance} />
          <SubScore label="Energy"          value={energy} />
          <SubScore label="Carbon"          value={carbon} />
          <SubScore label="Maintainability" value={maintainability} />
        </div>
      </div>
    </div>
  )
}
