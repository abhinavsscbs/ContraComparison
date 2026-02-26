import { useState } from 'react'
import { apiJson, downloadFromJson } from '../api'

export default function TaxPage() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  const run = async () => {
    if (!file) return
    setBusy(true)
    try {
      const form = new FormData()
      form.append('file', file)
      const data = await apiJson('/api/tax/analyze', { method: 'POST', body: form })
      setResult(data)
    } catch (e) {
      alert(e.message)
    } finally {
      setBusy(false)
    }
  }

  const exportExcel = async () => {
    await downloadFromJson('/api/tax/export/excel', result, 'enhanced_tax_analysis.xlsx')
  }

  const exportJson = async () => {
    await downloadFromJson('/api/tax/export/json', result, 'enhanced_tax_analysis.json')
  }

  return (
    <section>
      <h2>Enhanced Tax Analysis</h2>
      <input type="file" accept=".pdf,.docx,.doc" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button disabled={busy} onClick={run}>{busy ? 'Analyzing...' : 'Analyze Contract'}</button>

      {result && (
        <div>
          <h3>Executive Summary</h3>
          <p>{result.executive_summary}</p>

          <h3>Detailed Analysis</h3>
          <pre>{result.detailed_analysis}</pre>

          <h3>Clause Analyses ({result.total_clauses})</h3>
          {result.analysis_results?.map((row, idx) => (
            <div key={idx} className="card">
              <h4>{row.clause_data?.title}</h4>
              <div><strong>Category:</strong> {row.clause_data?.category}</div>
              <details>
                <summary>Clause Text</summary>
                <p>{row.clause_data?.full_text}</p>
              </details>
              <pre>{row.tax_analysis}</pre>
            </div>
          ))}

          <div className="row">
            <button onClick={exportExcel}>Export Excel</button>
            <button onClick={exportJson}>Export JSON</button>
          </div>
        </div>
      )}
    </section>
  )
}
