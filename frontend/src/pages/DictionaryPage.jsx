import { useEffect, useMemo, useState } from 'react'
import { apiJson } from '../api'

export default function DictionaryPage() {
  const [dict, setDict] = useState({})
  const [word, setWord] = useState('')
  const [replacement, setReplacement] = useState('')
  const [search, setSearch] = useState('')

  const load = async () => setDict(await apiJson('/api/dictionary'))

  useEffect(() => { load() }, [])

  const filtered = useMemo(() => {
    if (!search) return dict
    const q = search.toLowerCase()
    return Object.fromEntries(
      Object.entries(dict).filter(([k, v]) => k.toLowerCase().includes(q) || v.toLowerCase().includes(q))
    )
  }, [dict, search])

  const save = async () => {
    if (!word || !replacement) return
    const data = await apiJson('/api/dictionary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word, replacement, case_sensitive: false })
    })
    setDict(data)
    setWord('')
    setReplacement('')
  }

  const del = async (key) => setDict(await apiJson(`/api/dictionary/${encodeURIComponent(key)}`, { method: 'DELETE' }))

  const clear = async () => {
    if (!confirm('Clear entire dictionary?')) return
    setDict(await apiJson('/api/dictionary', { method: 'DELETE' }))
  }

  return (
    <section>
      <h2>Replacement Dictionary</h2>
      <div className="pair">
        <input placeholder="Word" value={word} onChange={(e) => setWord(e.target.value)} />
        <input placeholder="Replacement" value={replacement} onChange={(e) => setReplacement(e.target.value)} />
        <button onClick={save}>Add / Update</button>
      </div>

      <div className="row">
        <input placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} />
        <button onClick={clear}>Clear All</button>
        <a href="/api/dictionary/export?format=csv" target="_blank">Export CSV</a>
        <a href="/api/dictionary/export?format=json" target="_blank">Export JSON</a>
      </div>

      <div>
        {Object.entries(filtered).map(([k, v]) => (
          <div key={k} className="row">
            <code>{k}</code>
            <span>{v}</span>
            <button onClick={() => del(k)}>Delete</button>
          </div>
        ))}
      </div>
    </section>
  )
}
