import { Brain, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react'

export default function PlannerInfo({ plannerData }) {
  const { plan, reflection } = plannerData
  const agents = plan?.plan || []
  const parallel = plan?.parallel_phase || []

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
        <div style={{
          width:        32,
          height:       32,
          borderRadius: 'var(--radius-sm)',
          background:   'rgba(96,165,250,0.1)',
          border:       '1px solid rgba(96,165,250,0.25)',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'center',
        }}>
          <Brain size={16} color="var(--blue-400)" />
        </div>
        <div>
          <p className="section-label">Planner Agent (Orchestrator)</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
            Dynamic pipeline decisions — powered by Gemini
          </p>
        </div>
      </div>

      {/* Execution plan */}
      <div style={{ marginBottom: 16 }}>
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 10 }}>Execution plan</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          {agents.map((agent, i) => {
            const isParallel = parallel.includes(agent)
            return (
              <div key={agent} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  padding:      '6px 14px',
                  background:   isParallel ? 'rgba(96,165,250,0.08)' : 'rgba(34,197,94,0.08)',
                  border:       `1px solid ${isParallel ? 'rgba(96,165,250,0.25)' : 'var(--green-700)'}`,
                  borderRadius: 'var(--radius-sm)',
                  fontSize:     '0.76rem',
                  fontFamily:   'var(--font-mono)',
                  color:        isParallel ? 'var(--blue-400)' : 'var(--green-400)',
                }}>
                  {agent.replace('_agent', '')}
                  {isParallel && <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: 6 }}>∥ parallel</span>}
                </div>
                {i < agents.length - 1 && <ArrowRight size={13} color="var(--text-muted)" />}
              </div>
            )
          })}
        </div>
      </div>

      {/* Reasoning */}
      {plan?.reasoning && (
        <div style={{
          padding:      '12px 14px',
          background:   'var(--bg-surface)',
          borderRadius: 'var(--radius-sm)',
          border:       '1px solid var(--border)',
          marginBottom: 12,
        }}>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4 }}>Planning reasoning</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
            "{plan.reasoning}"
          </p>
        </div>
      )}

      {/* Reflection */}
      {reflection && (
        <div style={{
          padding:      '12px 14px',
          background:   reflection.anomaly_detected ? 'rgba(245,158,11,0.05)' : 'rgba(34,197,94,0.04)',
          borderRadius: 'var(--radius-sm)',
          border:       `1px solid ${reflection.anomaly_detected ? '#78350f' : 'var(--border)'}`,
          display:      'flex',
          gap:          10,
          alignItems:   'flex-start',
        }}>
          {reflection.anomaly_detected
            ? <AlertTriangle size={15} color="var(--amber-400)" style={{ flexShrink: 0, marginTop: 1 }} />
            : <CheckCircle  size={15} color="var(--green-400)"  style={{ flexShrink: 0, marginTop: 1 }} />
          }
          <div>
            <p style={{ fontSize: '0.75rem', fontWeight: 600, color: reflection.anomaly_detected ? 'var(--amber-400)' : 'var(--green-400)', marginBottom: 3 }}>
              {reflection.anomaly_detected ? 'Anomaly detected' : 'Results verified'}
              {reflection.confidence && <span style={{ fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>confidence: {reflection.confidence}</span>}
            </p>
            {reflection.reflection_note && (
              <p style={{ fontSize: '0.79rem', color: 'var(--text-secondary)' }}>
                {reflection.reflection_note}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
