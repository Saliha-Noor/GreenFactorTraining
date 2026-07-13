import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts'
import { TrendingDown } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background:   'var(--bg-card)',
      border:       '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding:      '12px 16px',
    }}>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 6 }}>Month {label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color, fontSize: '0.82rem', fontFamily: 'var(--font-mono)' }}>
          {p.name === 'current' ? 'Current' : 'Optimized'}: {p.value.toFixed(4)} kg CO₂
        </p>
      ))}
    </div>
  )
}

export default function CarbonProjection({ data }) {
  const { per_run_g, daily_runs_assumed, yearly_co2_kg, yearly_co2_kg_optimized, savings_percent } = data

  // Build 12-month projection data
  const monthlyData = Array.from({ length: 12 }, (_, i) => ({
    month:     i + 1,
    current:   +(yearly_co2_kg / 12 * (i + 1)).toFixed(6),
    optimized: +(yearly_co2_kg_optimized / 12 * (i + 1)).toFixed(6),
  }))

  const savedKg = yearly_co2_kg - yearly_co2_kg_optimized

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
        <p className="section-label">Carbon Cost Projection</p>
        <span className="pill pill-green">
          <TrendingDown size={11} />
          {savings_percent}% potential savings
        </span>
      </div>

      {/* Key stats */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
        {[
          { label: 'Per Run',          value: `${per_run_g.toExponential(3)} g`,  color: 'var(--text-primary)' },
          { label: 'Daily Runs',       value: daily_runs_assumed,                  color: 'var(--blue-400)' },
          { label: 'Yearly (Current)', value: `${yearly_co2_kg.toFixed(4)} kg`,   color: 'var(--amber-400)' },
          { label: 'Yearly (Optimized)',value: `${yearly_co2_kg_optimized.toFixed(4)} kg`, color: 'var(--green-400)' },
          { label: 'Annual Saving',    value: `${savedKg.toFixed(4)} kg`,          color: 'var(--green-400)' },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            flex:         1,
            minWidth:     110,
            padding:      '14px 16px',
            background:   'var(--bg-surface)',
            borderRadius: 'var(--radius-md)',
            border:       '1px solid var(--border)',
          }}>
            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: 5 }}>{label}</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', fontWeight: 700, color }}>
              {String(value)}
            </p>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={monthlyData}>
          <defs>
            <linearGradient id="gc" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="go" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false} tickLine={false}
            tickFormatter={v => `M${v}`}
          />
          <YAxis
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false} tickLine={false}
            tickFormatter={v => `${v.toFixed(3)}kg`}
            width={70}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="current"   stroke="#f59e0b" fill="url(#gc)" strokeWidth={2} name="current" />
          <Area type="monotone" dataKey="optimized" stroke="#22c55e" fill="url(#go)" strokeWidth={2} name="optimized" />
        </AreaChart>
      </ResponsiveContainer>

      <p style={{ marginTop: 12, fontSize: '0.73rem', color: 'var(--text-muted)', textAlign: 'center' }}>
        12-month cumulative CO₂ projection — current vs optimized code
      </p>
    </div>
  )
}
