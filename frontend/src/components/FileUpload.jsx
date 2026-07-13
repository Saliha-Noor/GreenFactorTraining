import { useState, useRef } from 'react'
import { Upload, FileCode, X, Zap } from 'lucide-react'

export default function FileUpload({ onAnalyze, loading }) {
  const [file, setFile]   = useState(null)
  const [drag, setDrag]   = useState(false)
  const inputRef          = useRef()

  const handleFile = (f) => {
    if (!f) return
    if (!f.name.endsWith('.py')) return alert('Only .py files are accepted.')
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDrag(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div className="card" style={{ padding: 32 }}>
      {/* Drop zone */}
      <div
        onClick={() => !file && inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        style={{
          border:       `2px dashed ${drag ? 'var(--green-500)' : file ? 'var(--green-700)' : 'var(--border)'}`,
          borderRadius: 'var(--radius-lg)',
          padding:      '40px 24px',
          textAlign:    'center',
          cursor:       file ? 'default' : 'pointer',
          transition:   'var(--transition)',
          background:   drag ? 'rgba(34,197,94,0.04)' : 'transparent',
          position:     'relative',
        }}
      >
        {file ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
            <div style={{
              width:        56,
              height:       56,
              borderRadius: 'var(--radius-md)',
              background:   'rgba(34,197,94,0.1)',
              border:       '1px solid var(--green-700)',
              display:      'flex',
              alignItems:   'center',
              justifyContent: 'center',
            }}>
              <FileCode size={26} color="var(--green-400)" />
            </div>
            <div>
              <p style={{ fontFamily: 'var(--font-mono)', color: 'var(--green-400)', fontSize: '0.9rem' }}>
                {file.name}
              </p>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
                {(file.size / 1024).toFixed(1)} KB • Python source
              </p>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); setFile(null) }}
              className="btn btn-outline"
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
            >
              <X size={14} /> Remove
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
            <div style={{
              width:        60,
              height:       60,
              borderRadius: 'var(--radius-lg)',
              background:   'rgba(34,197,94,0.07)',
              border:       '1px solid var(--border)',
              display:      'flex',
              alignItems:   'center',
              justifyContent: 'center',
            }}>
              <Upload size={26} color="var(--text-muted)" />
            </div>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500 }}>
                Drop your Python file here
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>
                or click to browse — .py files only
              </p>
            </div>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept=".py"
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />
      </div>

      {/* Analyze button */}
      <button
        className="btn btn-primary"
        onClick={() => file && onAnalyze(file)}
        disabled={!file || loading}
        style={{ width: '100%', justifyContent: 'center', marginTop: 20, padding: '13px' }}
      >
        {loading ? (
          <>
            <span className="spinner" />
            Running pipeline…
          </>
        ) : (
          <>
            <Zap size={17} />
            Analyze Code
          </>
        )}
      </button>

      {/* Pipeline steps indicator */}
      <div style={{ marginTop: 20, display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
        {['Code Analysis', 'Energy', 'Benchmark', 'SCI', 'Green AI'].map((step, i) => (
          <span key={step} className="pill pill-green" style={{ opacity: loading ? 1 : 0.45 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
              {i + 1}
            </span>
            {step}
          </span>
        ))}
      </div>
    </div>
  )
}
