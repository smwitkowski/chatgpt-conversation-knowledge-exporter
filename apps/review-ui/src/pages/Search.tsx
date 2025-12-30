import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

interface SearchResult {
  topics: Array<{ topic_id: number; name: string; score: number }>
  conversations: Array<{ conversation_id: string; title: string; project_name?: string; score: number }>
  atoms: Array<{ conversation_id: string; type: string; statement?: string; question?: string; topic: string; score: number }>
  docs: Array<{ conversation_id: string; doc_name: string; path: string; score: number }>
}

export default function Search() {
  const [searchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<SearchResult | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery)
    }
  }, [initialQuery])

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&limit=20`)
      const data = await response.json()
      setResults(data)
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    performSearch(query)
  }

  return (
    <div className="container">
      <h1>Search</h1>
      <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search topics, conversations, atoms, docs..."
            style={{
              flex: 1,
              padding: '10px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
            }}
          />
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {results && (
        <div>
          {results.topics.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Topics ({results.topics.length})</h2>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {results.topics.map((topic, i) => (
                  <li key={i} style={{ marginBottom: '10px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
                    <Link to={`/topics/${topic.topic_id}`} style={{ fontWeight: 'bold' }}>
                      {topic.name}
                    </Link>
                    <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
                      Score: {topic.score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.conversations.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Conversations ({results.conversations.length})</h2>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {results.conversations.map((conv, i) => (
                  <li key={i} style={{ marginBottom: '10px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
                    <Link to={`/conversations/${conv.conversation_id}`} style={{ fontWeight: 'bold' }}>
                      {conv.title || 'Untitled Conversation'}
                    </Link>
                    {conv.project_name && (
                      <span style={{ marginLeft: '10px', color: '#666' }}>{conv.project_name}</span>
                    )}
                    <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
                      Score: {conv.score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.atoms.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Atoms ({results.atoms.length})</h2>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {results.atoms.map((atom, i) => (
                  <li key={i} style={{ marginBottom: '10px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
                    <div>
                      <span className="badge badge-secondary" style={{ marginRight: '5px' }}>{atom.type}</span>
                      <span className="badge badge-primary">{atom.topic}</span>
                    </div>
                    <div style={{ marginTop: '5px' }}>
                      {atom.statement && <p>{atom.statement}</p>}
                      {atom.question && <p>{atom.question}</p>}
                    </div>
                    <div style={{ marginTop: '5px' }}>
                      <Link to={`/conversations/${atom.conversation_id}`} style={{ fontSize: '12px', color: '#666' }}>
                        View conversation →
                      </Link>
                      <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
                        Score: {atom.score.toFixed(2)}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.docs.length > 0 && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Documents ({results.docs.length})</h2>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {results.docs.map((doc, i) => (
                  <li key={i} style={{ marginBottom: '10px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
                    <Link to={`/conversations/${doc.conversation_id}`} style={{ fontWeight: 'bold' }}>
                      {doc.doc_name}
                    </Link>
                    <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
                      Score: {doc.score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.topics.length === 0 && results.conversations.length === 0 && results.atoms.length === 0 && results.docs.length === 0 && (
            <div className="card">
              <p style={{ textAlign: 'center', color: '#666' }}>No results found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
