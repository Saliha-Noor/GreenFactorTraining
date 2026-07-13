import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts'
import { Database } from 'lucide-react'

const LANG_COLORS = {
  Python: '#22c55e',
  C:      '#60a5fa',
  'C++':  '#a78bfa',
  Java:   '#f59e0b',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background:   'var(--bg-card)',
      border:       '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding:      '12px 16px',
      fontFamily:   'var(--font-mono)',
    }}>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginBottom: 4 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color, fontSize: '0.85rem' }}>
          {p.value.toFixed(1)} J
        </p>
      ))}
    </div>
  )
}

export default function BenchmarkComparison({ benchmarkData, langComparison }) {
  const chartData = langComparison.map(d => ({
    language:      d.language,
    energy_joules: d.energy_joules,
  }))

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
        <p className="section-label">RAPL Benchmark Comparison</p>
        <span className="pill pill-blue">
          <Database size={11} />
          Energy-Languages Dataset + Intel RAPL
        </span>
      </div>

      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 20 }}>
        Real energy measurements from bare-metal Intel hardware — task: <span style={{ color: 'var(--green-400)', fontFamily: 'var(--font-mono)' }}>{benchmarkData.task_type}</span>
      </p>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData} barCategoryGap="28%">
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis
            dataKey="language"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            axisLine={false} tickLine={false}
          />
          <YAxis
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false} tickLine={false}
            tickFormatter={v => `${v}J`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34,197,94,0.05)' }} />
          <Bar dataKey="energy_joules" radius={[5, 5, 0, 0]}>
            {chartData.map(entry => (
              <Cell key={entry.language} fill={LANG_COLORS[entry.language] || '#22c55e'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Detail table */}
      <div style={{ marginTop: 20, overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {['Language', 'Energy (J)', 'Time (s)', 'Memory (MB)'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.72rem', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {langComparison.map((row, i) => (
              <tr key={row.language} style={{ borderBottom: '1px solid var(--border)', background: i % 2 === 0 ? 'rgba(34,197,94,0.02)' : 'transparent' }}>
                <td style={{ padding: '10px 12px' }}>
                  <span style={{ color: LANG_COLORS[row.language] || 'var(--text-primary)', fontWeight: 600 }}>
                    {row.language}
                  </span>
                </td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                  {row.energy_joules.toFixed(1)}
                </td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                  {row.time_seconds.toFixed(2)}
                </td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                  {row.memory_mb.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
