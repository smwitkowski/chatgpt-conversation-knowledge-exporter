import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ConversationDetail as ConversationDetailType, DocInfo, Atom, DecisionAtom, OpenQuestion } from '../types'

export default function ConversationDetail() {
  const { conversationId } = useParams<{ conversationId: string }>()
  const navigate = useNavigate()
  const [conversation, setConversation] = useState<ConversationDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'docs' | 'facts' | 'decisions' | 'questions'>('docs')
  const [selectedDoc, setSelectedDoc] = useState<DocInfo | null>(null)
  const [docContent, setDocContent] = useState<string>('')
  const [filters, setFilters] = useState<{
    atomType?: string
    status?: string
    atomTopic?: string
  }>({})
  const [selectedAtomIds, setSelectedAtomIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!conversationId) return
    fetch(`/api/conversations/${conversationId}`)
      .then(res => res.json())
      .then(data => {
        setConversation(data)
        setLoading(false)
        // Auto-select first doc
        if (data.docs && data.docs.length > 0) {
          setSelectedDoc(data.docs[0])
        }
      })
      .catch(err => {
        console.error('Failed to load conversation:', err)
        setLoading(false)
      })
  }, [conversationId])

  useEffect(() => {
    if (!selectedDoc || !conversationId) return
    fetch(`/api/conversations/${conversationId}/doc/${selectedDoc.name}`)
      .then(res => res.text())
      .then(text => setDocContent(text))
      .catch(err => {
        console.error('Failed to load doc:', err)
        setDocContent('Failed to load document')
      })
  }, [selectedDoc, conversationId])

  const handleDownload = async () => {
    if (!conversationId) return
    try {
      const response = await fetch(`/api/bundles/conversation/${conversationId}`, { method: 'POST' })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const title = conversation?.title.replace(/\s+/g, '-') || 'conversation'
      a.download = `conversation-${conversationId.substring(0, 8)}-${title}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Failed to download bundle:', err)
      alert('Failed to download bundle')
    }
  }

  const handleExportSelectedAtoms = async () => {
    if (!conversationId || selectedAtomIds.size === 0) return
    try {
      const response = await fetch(`/api/conversations/${conversationId}/atoms/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ atom_ids: Array.from(selectedAtomIds) }),
      })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `atoms-${conversationId.substring(0, 8)}.jsonl`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Failed to export atoms:', err)
      alert('Failed to export atoms')
    }
  }

  const getFilteredAtoms = (atoms: (Atom | DecisionAtom | OpenQuestion)[]) => {
    return atoms.filter(atom => {
      if (filters.atomType && atom.type !== filters.atomType) return false
      if (filters.status && atom.status !== filters.status) return false
      if (filters.atomTopic && atom.topic !== filters.atomTopic) return false
      return true
    })
  }

  const getUniqueAtomTopics = (atoms: (Atom | DecisionAtom | OpenQuestion)[]) => {
    return Array.from(new Set(atoms.map(a => a.topic))).sort()
  }

  if (loading) {
    return <div className="container">Loading conversation...</div>
  }

  if (!conversation) {
    return <div className="container">Conversation not found</div>
  }

  return (
    <div className="container">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="btn btn-secondary">
          ← Back
        </button>
        <button onClick={handleDownload} className="btn">
          📦 Download Bundle
        </button>
      </div>
      <div className="card">
        <h1 className="page-title">{conversation.title || 'Untitled Conversation'}</h1>
        {conversation.project_name && (
          <p className="page-subtitle">Project: {conversation.project_name}</p>
        )}
        <div className="topic-badges">
          {conversation.topics.map((t, i) => (
            <span
              key={i}
              className={t.rank === 'primary' ? 'badge badge-primary' : 'badge badge-secondary'}
            >
              {t.name} ({t.score.toFixed(2)})
            </span>
          ))}
          {conversation.review_flag && <span className="badge badge-warning">⚠️ Needs Review</span>}
        </div>
      </div>
      <div className="card">
        <div className="tab-container">
          <button
            onClick={() => setActiveTab('docs')}
            className={`tab-button ${activeTab === 'docs' ? 'active' : ''}`}
          >
            📄 Docs ({conversation.docs.length})
          </button>
          <button
            onClick={() => setActiveTab('facts')}
            className={`tab-button ${activeTab === 'facts' ? 'active' : ''}`}
          >
            💡 Facts ({conversation.facts.length})
          </button>
          <button
            onClick={() => setActiveTab('decisions')}
            className={`tab-button ${activeTab === 'decisions' ? 'active' : ''}`}
          >
            ⚖️ Decisions ({conversation.decisions.length})
          </button>
          <button
            onClick={() => setActiveTab('questions')}
            className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
          >
            ❓ Questions ({conversation.questions.length})
          </button>
        </div>
        <div style={{ marginTop: '24px' }}>
        {activeTab === 'docs' && (
          <div>
            {conversation.docs.length > 0 ? (
              <div style={{ display: 'flex', gap: '32px' }}>
                <div className="doc-sidebar">
                  <h3>Documents</h3>
                  <ul className="doc-nav-list">
                    {conversation.docs.map((doc, i) => (
                      <li key={i} className="doc-nav-item">
                        <button
                          onClick={() => setSelectedDoc(doc)}
                          className={`doc-nav-button ${selectedDoc?.name === doc.name ? 'active' : ''}`}
                        >
                          {doc.name}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
                <div style={{ flex: 1 }}>
                  {selectedDoc && (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{docContent}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p>No documents available</p>
            )}
          </div>
        )}
        {activeTab === 'facts' && (
          <div>
            <div className="filter-controls">
              <select
                value={filters.atomType || ''}
                onChange={(e) => setFilters({ ...filters, atomType: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Types</option>
                <option value="fact">Fact</option>
                <option value="requirement">Requirement</option>
                <option value="definition">Definition</option>
                <option value="metric">Metric</option>
                <option value="risk">Risk</option>
                <option value="assumption">Assumption</option>
                <option value="constraint">Constraint</option>
                <option value="idea">Idea</option>
              </select>
              <select
                value={filters.status || ''}
                onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="deprecated">Deprecated</option>
                <option value="uncertain">Uncertain</option>
              </select>
              <select
                value={filters.atomTopic || ''}
                onChange={(e) => setFilters({ ...filters, atomTopic: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Topics</option>
                {getUniqueAtomTopics(conversation.facts).map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
              {selectedAtomIds.size > 0 && (
                <button onClick={handleExportSelectedAtoms} className="btn" style={{ marginLeft: 'auto' }}>
                  📥 Export Selected ({selectedAtomIds.size})
                </button>
              )}
            </div>
            {conversation.facts.length > 0 ? (
              <div>
                {getFilteredAtoms(conversation.facts).map((fact, i) => {
                  const atomId = `${conversationId}-fact-${i}`
                  return (
                  <div key={i} className={`atom-card ${selectedAtomIds.has(atomId) ? 'selected' : ''}`}>
                    <div className="atom-header">
                      <input
                        type="checkbox"
                        checked={selectedAtomIds.has(atomId)}
                        onChange={(e) => {
                          const newSet = new Set(selectedAtomIds)
                          if (e.target.checked) {
                            newSet.add(atomId)
                          } else {
                            newSet.delete(atomId)
                          }
                          setSelectedAtomIds(newSet)
                        }}
                      />
                      <span className="badge badge-primary">{fact.topic}</span>
                      <span className={`badge ${fact.status === 'active' ? 'badge-primary' : 'badge-secondary'}`}>
                        {fact.status}
                      </span>
                      <span className="badge badge-secondary">{fact.type}</span>
                    </div>
                    <div className="atom-content">{fact.statement}</div>
                    {fact.evidence && fact.evidence.length > 0 && (
                      <details>
                        <summary>📎 Evidence ({fact.evidence.length})</summary>
                        <div className="atom-meta">
                          <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                            {fact.evidence.map((ev, j) => (
                              <li key={j} style={{ marginBottom: '6px' }}>
                                {ev.message_id && <code>{ev.message_id}</code>}
                                {ev.time_iso && <span> at {ev.time_iso}</span>}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </details>
                    )}
                  </div>
                  )
                })}
                {getFilteredAtoms(conversation.facts).length === 0 && (
                  <p>No facts match the selected filters</p>
                )}
              </div>
            ) : (
              <p>No facts available</p>
            )}
          </div>
        )}
        {activeTab === 'decisions' && (
          <div>
            <div className="filter-controls">
              <select
                value={filters.status || ''}
                onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="deprecated">Deprecated</option>
                <option value="uncertain">Uncertain</option>
              </select>
              <select
                value={filters.atomTopic || ''}
                onChange={(e) => setFilters({ ...filters, atomTopic: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Topics</option>
                {getUniqueAtomTopics(conversation.decisions).map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
              {selectedAtomIds.size > 0 && (
                <button onClick={handleExportSelectedAtoms} className="btn" style={{ marginLeft: 'auto' }}>
                  📥 Export Selected ({selectedAtomIds.size})
                </button>
              )}
            </div>
            {conversation.decisions.length > 0 ? (
              <div>
                {getFilteredAtoms(conversation.decisions).map((decision, i) => {
                  const atomId = `${conversationId}-decision-${i}`
                  return (
                  <div key={i} className={`atom-card ${selectedAtomIds.has(atomId) ? 'selected' : ''}`}>
                    <div className="atom-header">
                      <input
                        type="checkbox"
                        checked={selectedAtomIds.has(atomId)}
                        onChange={(e) => {
                          const newSet = new Set(selectedAtomIds)
                          if (e.target.checked) {
                            newSet.add(atomId)
                          } else {
                            newSet.delete(atomId)
                          }
                          setSelectedAtomIds(newSet)
                        }}
                      />
                      <span className="badge badge-primary">{decision.topic}</span>
                      <span className={`badge ${decision.status === 'active' ? 'badge-primary' : 'badge-secondary'}`}>
                        {decision.status}
                      </span>
                    </div>
                    <div className="atom-content" style={{ fontWeight: '600', fontSize: '16px' }}>
                      {decision.statement}
                    </div>
                    {decision.rationale && (
                      <div className="atom-meta">
                        <strong>Rationale:</strong> {decision.rationale}
                      </div>
                    )}
                    {decision.alternatives && decision.alternatives.length > 0 && (
                      <div className="atom-meta">
                        <strong>Alternatives Considered:</strong>
                        <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
                          {decision.alternatives.map((alt, j) => (
                            <li key={j}>{alt}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {decision.consequences && (
                      <div className="atom-meta" style={{ marginTop: '8px' }}>
                        <strong>Consequences:</strong> {decision.consequences}
                      </div>
                    )}
                  </div>
                  )
                })}
                {getFilteredAtoms(conversation.decisions).length === 0 && (
                  <p>No decisions match the selected filters</p>
                )}
              </div>
            ) : (
              <p>No decisions available</p>
            )}
          </div>
        )}
        {activeTab === 'questions' && (
          <div>
            <div className="filter-controls">
              <select
                value={filters.atomTopic || ''}
                onChange={(e) => setFilters({ ...filters, atomTopic: e.target.value || undefined })}
                className="filter-select"
              >
                <option value="">All Topics</option>
                {getUniqueAtomTopics(conversation.questions).map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
              {selectedAtomIds.size > 0 && (
                <button onClick={handleExportSelectedAtoms} className="btn" style={{ marginLeft: 'auto' }}>
                  📥 Export Selected ({selectedAtomIds.size})
                </button>
              )}
            </div>
            {conversation.questions.length > 0 ? (
              <div>
                {getFilteredAtoms(conversation.questions).map((question, i) => {
                  const atomId = `${conversationId}-question-${i}`
                  return (
                  <div key={i} className={`atom-card ${selectedAtomIds.has(atomId) ? 'selected' : ''}`}>
                    <div className="atom-header">
                      <input
                        type="checkbox"
                        checked={selectedAtomIds.has(atomId)}
                        onChange={(e) => {
                          const newSet = new Set(selectedAtomIds)
                          if (e.target.checked) {
                            newSet.add(atomId)
                          } else {
                            newSet.delete(atomId)
                          }
                          setSelectedAtomIds(newSet)
                        }}
                      />
                      <span className="badge badge-primary">{question.topic}</span>
                    </div>
                    <div className="atom-content" style={{ fontWeight: '600', fontSize: '16px' }}>
                      {question.question}
                    </div>
                    {question.context && (
                      <div className="atom-meta">
                        <strong>Context:</strong> {question.context}
                      </div>
                    )}
                  </div>
                  )
                })}
                {getFilteredAtoms(conversation.questions).length === 0 && (
                  <p>No questions match the selected filters</p>
                )}
              </div>
            ) : (
              <p>No questions available</p>
            )}
          </div>
        )}
        </div>
      </div>
    </div>
  )
}
