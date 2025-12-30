import { useState, useEffect } from 'react'
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'
import TopicList from './pages/TopicList'
import TopicDetail from './pages/TopicDetail'
import ConversationDetail from './pages/ConversationDetail'
import ReviewQueue from './pages/ReviewQueue'
import Search from './pages/Search'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  const location = useLocation()

  // Sync search query with URL
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const q = params.get('q')
    if (q && location.pathname === '/search') {
      setSearchQuery(q)
    }
  }, [location])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <div>
      <nav style={{ background: '#333', color: 'white', padding: '16px' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '20px' }}>
          <Link to="/" style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
            Topic Review
          </Link>
          <form onSubmit={handleSearchSubmit} style={{ flex: 1, maxWidth: '400px' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              style={{
                width: '100%',
                padding: '8px',
                border: 'none',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            />
          </form>
          <div>
            <Link to="/" style={{ color: 'white', marginRight: '20px' }}>Topics</Link>
            <Link to="/review-queue" style={{ color: 'white', marginRight: '20px' }}>Review Queue</Link>
            <Link to="/search" style={{ color: 'white' }}>Search</Link>
          </div>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<TopicList />} />
        <Route path="/topics/:topicId" element={<TopicDetail />} />
        <Route path="/conversations/:conversationId" element={<ConversationDetail />} />
        <Route path="/review-queue" element={<ReviewQueue />} />
        <Route path="/search" element={<Search />} />
      </Routes>
    </div>
  )
}

export default App
