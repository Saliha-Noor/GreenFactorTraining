import { useState } from 'react'
import { Leaf, AlertCircle } from 'lucide-react'

import Header             from './components/Header.jsx'
import FileUpload         from './components/FileUpload.jsx'
import GreenScore         from './components/GreenScore.jsx'
import EnergyMetrics      from './components/EnergyMetrics.jsx'
import BenchmarkComparison from './components/BenchmarkComparison.jsx'
import SCIScores          from './components/SCIScores.jsx'
import CarbonProjection   from './components/CarbonProjection.jsx'
import PlannerInfo        from './components/PlannerInfo.jsx'
import DownloadReport     from './components/DownloadReport.jsx'
import { analyzeCode }    from './utils/api.js'

const STEPS = [
  'Parsing code structure…',
  'Building execution plan…',
  'Measuring energy (CodeCarbon)…',
  'Fetching RAPL benchmarks…',
  'Calculating SCI scores…',
  'Planner reflecting on results…',
  'Generating Green Score & Carbon Projection…',
  'Finalizing report…',
]

export default function App() {
  const [result,    setResult]    = useState(null)
  const [file,      setFile]      = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [step,      setStep]      = useState(0)
  const [error,     setError]     = useState(null)

  const handleAnalyze = async (uploadedFile) => {
    setFile(uploadedFile)
    setResult(null)
    setError(null)
    setLoading(true)
    setStep(0)

    // Simulate pipeline step progression
    const interval = setInterval(() => {
      setStep(s => (s < STEPS.length - 1 ? s + 1 : s))
    }, 900)

    try {
      const data = await analyzeCode(uploadedFile)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      clearInterval(interval)
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />

      <main style={{ flex: 1, maxWidth: 1100, margin: '0 auto', width: '100%', padding: '40px 24px 80px' }}>

        {/* Hero */}
        {!result && !loading && (
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 22 }}>
              <div style={{
                width:        50,
                height:       50,
                borderRadius: 16,
                background:   'linear-gradient(135deg, #166116, #0a3d0a)',
                border:       '1px solid var(--green-700)',
                display:      'flex',
                alignItems:   'center',
                justifyContent: 'center',
                boxShadow:    '0 0 32px rgba(34,197,94,0.2)',
              }}>
                <Leaf size={24} color="var(--green-400)" />
              </div>
            </div>

            <h1 style={{
              fontFamily:    'var(--font-display)',
              fontSize:      'clamp(2rem, 5vw, 3.2rem)',
              fontWeight:    800,
              color:         'var(--text-primary)',
              letterSpacing: '-0.02em',
              lineHeight:    1.15,
              marginBottom:  16,
            }}>
              Measure the carbon cost<br />
              <span style={{ color: 'var(--green-400)' }}>of your Python code.</span>
            </h1>

            <p style={{
              fontSize:   '1.05rem',
              color:      'var(--text-secondary)',
              maxWidth:   560,
              margin:     '0 auto 36px',
              lineHeight: 1.7,
            }}>
              A 5-agent AI pipeline that analyzes energy consumption, compares against real Intel RAPL benchmarks, and scores your code's sustainability — evidence-based, not guesswork.
            </p>

            {/* Agent pipeline visualization */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: 0, marginBottom: 48, flexWrap: 'wrap' }}>
              {[
                { name: 'Code Analysis', color: '#60a5fa' },
                { name: 'Energy',        color: '#22c55e' },
                { name: 'Benchmark',     color: '#a78bfa' },
                { name: 'SCI',           color: '#f59e0b' },
                { name: 'Recommendation',color: '#22c55e' },
              ].map((agent, i) => (
                <div key={agent.name} style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{
                    padding:      '7px 16px',
                    background:   `${agent.color}10`,
                    border:       `1px solid ${agent.color}30`,
                    borderRadius: 'var(--radius-sm)',
                    fontSize:     '0.78rem',
                    color:        agent.color,
                    fontWeight:   500,
                    whiteSpace:   'nowrap',
                  }}>
                    {agent.name}
                  </div>
                  {i < 4 && (
                    <div style={{
                      width:      28,
                      height:     1,
                      background: 'var(--border)',
                    }} />
                  )}
                </div>
              ))}
            </div>

            <div style={{ maxWidth: 540, margin: '0 auto' }}>
              <FileUpload onAnalyze={handleAnalyze} loading={loading} />
            </div>
          </div>
        )}

        {/* Upload section (when result exists — compact) */}
        {(result || loading) && (
          <div style={{ maxWidth: 540, margin: '0 auto 40px' }}>
            <FileUpload onAnalyze={handleAnalyze} loading={loading} />
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div style={{
            textAlign:    'center',
            padding:      '60px 24px',
            maxWidth:     500,
            margin:       '0 auto',
          }}>
            <div style={{
              width:        64,
              height:       64,
              borderRadius: '50%',
              background:   'rgba(34,197,94,0.08)',
              border:       '2px solid var(--green-700)',
              display:      'flex',
              alignItems:   'center',
              justifyContent: 'center',
              margin:       '0 auto 24px',
              animation:    'pulse-green 2s ease-in-out infinite',
            }}>
              <Leaf size={28} color="var(--green-400)" />
            </div>

            <div style={{ marginBottom: 24 }}>
              {STEPS.map((s, i) => (
                <div key={i} style={{
                  display:      'flex',
                  alignItems:   'center',
                  gap:          10,
                  padding:      '7px 0',
                  opacity:      i <= step ? 1 : 0.25,
                  transition:   'opacity 0.5s ease',
                }}>
                  <div style={{
                    width:        18,
                    height:       18,
                    borderRadius: '50%',
                    background:   i < step  ? 'var(--green-500)'
                                : i === step ? 'var(--green-700)' : 'var(--border)',
                    border:       i === step ? '2px solid var(--green-400)' : 'none',
                    flexShrink:   0,
                    transition:   'background 0.4s',
                  }} />
                  <span style={{
                    fontSize:   '0.85rem',
                    color:      i <= step ? 'var(--text-primary)' : 'var(--text-muted)',
                    fontFamily: i === step ? 'var(--font-mono)' : 'var(--font-body)',
                  }}>
                    {s}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            maxWidth:     600,
            margin:       '0 auto 32px',
            padding:      '16px 20px',
            background:   'rgba(239,68,68,0.07)',
            border:       '1px solid rgba(239,68,68,0.25)',
            borderRadius: 'var(--radius-md)',
            display:      'flex',
            gap:          12,
            alignItems:   'flex-start',
          }}>
            <AlertCircle size={18} color="var(--red-500)" style={{ flexShrink: 0, marginTop: 1 }} />
            <div>
              <p style={{ color: 'var(--red-500)', fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>Analysis failed</p>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Top row: Green Score + SCI */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
              <GreenScore data={result.recommendation.green_score} />
              <SCIScores  sciScores={result.sci_scores} />
            </div>

            {/* Energy + Code stats */}
            <EnergyMetrics energyData={result.energy_data} codeStats={result.code_stats} />

            {/* Benchmark */}
            <BenchmarkComparison
              benchmarkData={result.benchmark_data}
              langComparison={result.lang_comparison}
            />

            {/* Carbon projection */}
            <CarbonProjection data={result.recommendation.carbon_projection} />

            {/* Planner */}
            <PlannerInfo plannerData={result.planner} />

            {/* Download */}
            <DownloadReport file={file} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding:   '20px 24px',
        textAlign: 'center',
      }}>
        <p style={{ fontSize: '0.77rem', color: 'var(--text-muted)' }}>
          GreenDev AI — Evidence-based green code analysis ·{' '}
          <span style={{ color: 'var(--green-700)' }}>5-agent pipeline</span> ·
          CodeCarbon + Energy-Languages Dataset + Gemini API
        </p>
      </footer>
    </div>
  )
}
