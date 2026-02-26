import { useState } from 'react'
import ComparisonPage from './pages/ComparisonPage'
import DictionaryPage from './pages/DictionaryPage'
import TaxPage from './pages/TaxPage'

const tabs = [
  'Contract Comparison',
  'Replacement Dictionary',
  'Enhanced Tax Analysis'
]

export default function App() {
  const [tab, setTab] = useState(tabs[0])

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Contract Suite</h1>
        {tabs.map((t) => (
          <button
            key={t}
            className={tab === t ? 'nav active' : 'nav'}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </aside>

      <main className="content">
        {tab === 'Contract Comparison' && <ComparisonPage />}
        {tab === 'Replacement Dictionary' && <DictionaryPage />}
        {tab === 'Enhanced Tax Analysis' && <TaxPage />}
      </main>
    </div>
  )
}
