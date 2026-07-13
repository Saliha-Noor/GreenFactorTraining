import { AlertTriangle, CheckCircle } from 'lucide-react'

function SciCard({ label, value, sub }) {
  return (
    <div style={{
      flex:         1,
      minWidth:     160,
      padding:      '20px',
      background:   'var(--bg-surface)',
      borderRadius: 'var(--radius-md)',
      border:       '1px solid var(--border)',
    }}>
      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        {label}
      </p>
      <p style={{
        fontFamily:  'var(--font-mono)',
        fontSize:    '1.35rem',
        fontWeight:  700,
        color:       'var(--green-400)',
        lineHeight:  1,
        marginBottom: 6,
      }}>
        {typeof value === 'number' ? value.toExponential(4) : value}
      </p>
      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{sub}</p>
    </div>
  )
}

export default function SCIScores({ sciScores }) {
  const { estimated_sci, real_sci, deviation_pct, anomaly_detected, carbon_intensity } = sciScores

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
        <p className="section-label">SCI Scores</p>
        <span className={`pill ${anomaly_detected ? 'pill-amber' : 'pill-green'}`}>
          {anomaly_detected
            ? <><AlertTriangle size={11} /> Anomaly Detected</>
            : <><CheckCircle size={11} /> Normal</>
          }
        </span>
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
        <SciCard label="Estimated SCI (CodeCarbon)" value={estimated_sci} sub="gCO₂eq per run — from your hardware" />
        <SciCard label="Real SCI (RAPL Dataset)"    value={real_sci}     sub="gCO₂eq per run — bare-metal Intel" />
      </div>

      {/* Deviation bar */}
      <div style={{
        padding:      '14px 16px',
        background:   'var(--bg-surface)',
        borderRadius: 'var(--radius-md)',
        border:       `1px solid ${anomaly_detected ? '#78350f' : 'var(--border)'}`,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Deviation between Estimated vs Real</span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   '0.85rem',
            fontWeight: 700,
            color:      anomaly_detected ? 'var(--amber-400)' : 'var(--green-400)',
          }}>
            {deviation_pct}%
          </span>
        </div>
        <div style={{ height: 6, borderRadius: 99, background: 'var(--bg-base)', overflow: 'hidden' }}>
          <div style={{
            height:     '100%',
            width:      `${Math.min(deviation_pct, 100)}%`,
            background: anomaly_detected ? 'var(--amber-500)' : 'var(--green-500)',
            borderRadius: 99,
            transition: 'width 1s ease',
          }} />
        </div>
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 8 }}>
          Grid carbon intensity: {carbon_intensity} gCO₂eq/kWh
          {anomaly_detected && ' · Large deviation detected — results may vary from real hardware'}
        </p>
      </div>
    </div>
  )
}
