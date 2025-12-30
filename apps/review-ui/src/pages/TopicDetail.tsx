import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { TopicDetail as TopicDetailType, ConversationSummary } from '../types'
import AddonPanel from '../components/AddonPanel'

export default function TopicDetail() {
  const { topicId } = useParams<{ topicId: string }>()
  const navigate = useNavigate()
  const [topic, setTopic] = useState<TopicDetailType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!topicId) return
    fetch(`/api/topics/${topicId}`)
      .then(res => res.json())
      .then(data => {
        setTopic(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load topic:', err)
        setLoading(false)
      })
  }, [topicId])

  const handleDownload = async () => {
    if (!topicId) return
    try {
      const response = await fetch(`/api/bundles/topic/${topicId}`, { method: 'POST' })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `topic-${topicId}-${topic?.name.replace(/\s+/g, '-') || 'unknown'}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Failed to download bundle:', err)
      alert('Failed to download bundle')
    }
  }

  if (loading) {
    return <div className="container">Loading topic...</div>
  }

  if (!topic) {
    return <div className="container">Topic not found</div>
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => navigate(-1)} className="btn btn-secondary" style={{ marginRight: '10px' }}>
          ← Back
        </button>
        <button onClick={handleDownload} className="btn">
          Download Topic Bundle
        </button>
      </div>
      <div className="card">
        <h1>{topic.name}</h1>
        <p style={{ marginTop: '10px', color: '#666' }}>{topic.description}</p>
        <div style={{ marginTop: '15px' }}>
          <strong>Keywords:</strong>{' '}
          {topic.keywords.map((kw, i) => (
            <span key={i} className="badge badge-secondary" style={{ marginLeft: '5px' }}>
              {kw}
            </span>
          ))}
        </div>
        <div style={{ marginTop: '15px' }}>
          <strong>Stats:</strong> {topic.conversation_count} conversations, {topic.atom_count} atoms
          {topic.flagged_count > 0 && (
            <span className="badge badge-warning" style={{ marginLeft: '10px' }}>
              {topic.flagged_count} flagged
            </span>
          )}
        </div>
      </div>
      <div className="card">
        <h2>Conversations</h2>
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Project</th>
              <th>Topics</th>
              <th>Atoms</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {topic.conversations.map(conv => (
              <tr key={conv.conversation_id}>
                <td>
                  <Link to={`/conversations/${conv.conversation_id}`}>
                    {conv.title || 'Untitled Conversation'}
                  </Link>
                </td>
                <td>{conv.project_name || '-'}</td>
                <td>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {conv.topics.map((t, i) => (
                      <span
                        key={i}
                        className={t.rank === 'primary' ? 'badge badge-primary' : 'badge badge-secondary'}
                      >
                        {t.name} ({t.score.toFixed(2)})
                      </span>
                    ))}
                  </div>
                </td>
                <td>{conv.atom_count}</td>
                <td>
                  {conv.review_flag && <span className="badge badge-warning">Review</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <AddonPanel targetKind="topic" targetId={topicId} />
    </div>
  )
}
