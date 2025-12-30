import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { TopicSummary } from '../types'

export default function TopicList() {
  const [topics, setTopics] = useState<TopicSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetch('/api/topics')
      .then(res => res.json())
      .then(data => {
        setTopics(data.topics || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load topics:', err)
        setLoading(false)
      })
  }, [])

  const filteredTopics = topics.filter(topic =>
    topic.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    topic.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    topic.keywords.some(kw => kw.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  if (loading) {
    return <div className="container">Loading topics...</div>
  }

  return (
    <div className="container">
      <h1>Topics</h1>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search topics..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
          }}
        />
      </div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Topic</th>
              <th>Description</th>
              <th>Keywords</th>
              <th>Conversations</th>
              <th>Atoms</th>
              <th>Flagged</th>
            </tr>
          </thead>
          <tbody>
            {filteredTopics.map(topic => (
              <tr key={topic.topic_id}>
                <td>
                  <Link to={`/topics/${topic.topic_id}`} style={{ fontWeight: 'bold' }}>
                    {topic.name}
                  </Link>
                </td>
                <td>{topic.description}</td>
                <td>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {topic.keywords.slice(0, 5).map((kw, i) => (
                      <span key={i} className="badge badge-secondary">{kw}</span>
                    ))}
                    {topic.keywords.length > 5 && <span>...</span>}
                  </div>
                </td>
                <td>{topic.conversation_count}</td>
                <td>{topic.atom_count}</td>
                <td>
                  {topic.flagged_count > 0 && (
                    <span className="badge badge-warning">{topic.flagged_count}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredTopics.length === 0 && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            No topics found
          </div>
        )}
      </div>
    </div>
  )
}
