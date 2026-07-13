const BASE = 'http://localhost:8000'

export async function analyzeCode(file) {
  const form = new FormData()
  form.append('file', file)

  const res = await fetch(`${BASE}/analyze`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `Server error ${res.status}`)
  }
  return res.json()
}

export function downloadPdfUrl()      { return `${BASE}/report/pdf` }
export function downloadMarkdownUrl() { return `${BASE}/report/markdown` }

export async function downloadReport(file, format = 'pdf') {
  const form = new FormData()
  form.append('file', file)

  const url = format === 'pdf' ? downloadPdfUrl() : downloadMarkdownUrl()
  const res = await fetch(url, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Report generation failed')

  const blob     = await res.blob()
  const blobUrl  = window.URL.createObjectURL(blob)
  const link     = document.createElement('a')
  link.href      = blobUrl
  link.download  = `greendev_report.${format === 'pdf' ? 'pdf' : 'md'}`
  link.click()
  window.URL.revokeObjectURL(blobUrl)
}
