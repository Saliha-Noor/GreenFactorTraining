import { Zap, Wind, Clock } from 'lucide-react'

function Stat({ icon: Icon, label, value, unit, color = 'var(--green-400)' }) {
  return (
    <div style={{
      flex:        1,
      minWidth:    140,
      padding:     '18px 20px',
      background:  'var(--bg-surface)',
      borderRadius: 'var(--radius-md)',
      border:      '1px solid var(--border)',
      display:     'flex',
      flexDirection: 'column',
      gap:         10,
    }}>
      <div style={{
        width:        36,
        height:       36,
        borderRadius: 'var(--radius-sm)',
        background:   `${color}14`,
        border:       `1px solid ${color}33`,
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'center',
      }}>
        <Icon size={17} color={color} />
      </div>
      <div>
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4 }}>{label}</p>
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize:   '1rem',
          fontWeight: 600,
          color:      'var(--text-primary)',
        }}>
          {value}
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: 5 }}>{unit}</span>
        </p>
      </div>
    </div>
  )
}

export default function EnergyMetrics({ energyData, codeStats }) {
  const fmtEnergy = (v) => {
    if (v < 0.000001) return (v * 1e9).toFixed(4) + ' nWh'
    if (v < 0.001)    return (v * 1e6).toFixed(4) + ' µWh'
    return v.toFixed(6) + ' kWh'
  }

  const fmtCo2 = (v) => {
    if (v < 0.001) return (v * 1e6).toFixed(4) + ' µg'
    if (v < 1)     return (v * 1000).toFixed(4) + ' mg'
    return v.toFixed(4) + ' g'
  }

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
        <p className="section-label">Energy Measurement</p>
        <span className="pill pill-blue">{energyData.mode}</span>
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Stat icon={Zap}   label="Energy Consumed" value={fmtEnergy(energyData.energy_kwh)} unit="" color="var(--green-400)" />
        <Stat icon={Wind}  label="CO₂ Emitted"     value={fmtCo2(energyData.co2_grams)}    unit="" color="var(--amber-400)" />
        <Stat icon={Clock} label="Execution Time"  value={energyData.execution_time}        unit="s" color="var(--blue-400)" />
      </div>

      {/* Code stats row */}
      <div style={{
        marginTop:    16,
        padding:      '14px 18px',
        background:   'var(--bg-surface)',
        borderRadius: 'var(--radius-md)',
        border:       '1px solid var(--border)',
        display:      'flex',
        gap:          28,
        flexWrap:     'wrap',
      }}>
        {[
          ['Functions',  codeStats.functions],
          ['Loops',      codeStats.loops],
          ['Nested',     codeStats.nested_loops],
          ['Lines',      codeStats.lines],
          ['Complexity', codeStats.complexity],
          ['Task',       codeStats.task_type],
        ].map(([k, v]) => (
          <div key={k}>
            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: 3 }}>{k}</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', color: 'var(--text-primary)', fontWeight: 600 }}>
              {String(v)}
            </p>
          </div>
        ))}
      </div>

      {/* Execution output */}
      {energyData.stdout && (
        <div style={{ marginTop: 14 }}>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6 }}>Code Output</p>
          <pre style={{
            fontFamily:   'var(--font-mono)',
            fontSize:     '0.78rem',
            color:        'var(--text-code)',
            background:   'var(--bg-input)',
            border:       '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding:      '12px 14px',
            overflowX:    'auto',
            maxHeight:    120,
            overflowY:    'auto',
          }}>
            {energyData.stdout.slice(0, 800)}
          </pre>
        </div>
      )}
    </div>
  )
}
