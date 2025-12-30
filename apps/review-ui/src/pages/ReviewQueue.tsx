import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ReviewQueueItem } from '../types'

export default function ReviewQueue() {
  const [items, setItems] = useState<ReviewQueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const loadQueue = async () => {
    try {
      const response = await fetch('/api/review-queue')
      const data = await response.json()
      setItems(data.items || [])
    } catch (err) {
      console.error('Failed to load review queue:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQueue()
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await fetch('/api/refresh', { method: 'POST' })
      await loadQueue()
    } catch (err) {
      console.error('Failed to refresh:', err)
      alert('Failed to refresh index')
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return <div className="container">Loading review queue...</div>
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1>Review Queue</h1>
          <p style={{ marginTop: '5px', color: '#666' }}>
            Conversations flagged for manual review due to low confidence or ambiguous topic assignments.
          </p>
        </div>
        <button onClick={handleRefresh} className="btn" disabled={refreshing}>
          {refreshing ? 'Refreshing...' : 'Refresh Index'}
        </button>
      </div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Project</th>
              <th>Primary Topic</th>
              <th>Score</th>
              <th>Reason</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.conversation_id}>
                <td>
                  <Link to={`/conversations/${item.conversation_id}`}>
                    {item.title || 'Untitled Conversation'}
                  </Link>
                </td>
                <td>{item.project_name || '-'}</td>
                <td>{item.primary_topic}</td>
                <td>
                  <span className={item.primary_score < 0.6 ? 'badge badge-warning' : 'badge badge-secondary'}>
                    {item.primary_score.toFixed(3)}
                  </span>
                </td>
                <td>
                  <span className="badge badge-warning">{item.reason}</span>
                </td>
                <td>
                  <Link to={`/conversations/${item.conversation_id}`} className="btn" style={{ fontSize: '12px', padding: '4px 8px' }}>
                    Review
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            No items in review queue
          </div>
        )}
      </div>
    </div>
  )
}
