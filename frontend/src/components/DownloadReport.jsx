import { useState } from 'react'
import { FileDown, FileText, Loader } from 'lucide-react'
import { downloadReport } from '../utils/api'

export default function DownloadReport({ file }) {
  const [loading, setLoading] = useState(null)
  const [error,   setError]   = useState(null)

  const handle = async (format) => {
    setLoading(format)
    setError(null)
    try {
      await downloadReport(file, format)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="card fade-in" style={{ padding: 28 }}>
      <p className="section-label" style={{ marginBottom: 16 }}>Download Full Report</p>

      <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: 20 }}>
        Export a complete sustainability report containing all agent outputs — code stats, energy measurements, RAPL benchmarks, SCI scores, Green Score, and Carbon Projection.
      </p>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          onClick={() => handle('pdf')}
          disabled={loading !== null}
          style={{ flex: 1, justifyContent: 'center', minWidth: 160 }}
        >
          {loading === 'pdf'
            ? <><Loader size={16} style={{ animation: 'spin 0.8s linear infinite' }} /> Generating PDF…</>
            : <><FileDown size={16} /> Download PDF</>
          }
        </button>

        <button
          className="btn btn-outline"
          onClick={() => handle('markdown')}
          disabled={loading !== null}
          style={{ flex: 1, justifyContent: 'center', minWidth: 160 }}
        >
          {loading === 'markdown'
            ? <><Loader size={16} style={{ animation: 'spin 0.8s linear infinite' }} /> Generating…</>
            : <><FileText size={16} /> Download Markdown</>
          }
        </button>
      </div>

      {error && (
        <p style={{ marginTop: 12, fontSize: '0.8rem', color: 'var(--red-500)' }}>
          ⚠ {error}
        </p>
      )}
    </div>
  )
}
