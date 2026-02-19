import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const YOUR_ARTICLE_TITLE = 'ASET'

function App() {
  const [leaderboard, setLeaderboard] = useState([])
  const [hostArticles, setHostArticles] = useState([])
  const [stats, setStats] = useState(null)
  const [yourArticle, setYourArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showHost, setShowHost] = useState(false)
  const [showCookieModal, setShowCookieModal] = useState(false)
  const [cookieText, setCookieText] = useState('')
  const [cookieStatus, setCookieStatus] = useState(null)
  const [dataLoading, setDataLoading] = useState(false)
  const [sortBy, setSortBy] = useState('engagement_score')

  useEffect(() => {
    checkCookieStatus()
  }, [])

  useEffect(() => {
    if (cookieStatus?.status === 'valid') {
      fetchData()
    }
  }, [cookieStatus])

  const fetchData = async () => {
    try {
      setDataLoading(true)
      
      await fetch(`${API_BASE}/refresh`, { method: 'POST' })
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const leaderboardRes = await fetch(`${API_BASE}/leaderboard?exclude_host=true`)
      if (!leaderboardRes.ok) throw new Error('Failed to fetch leaderboard')
      const leaderboardData = await leaderboardRes.json()
      setLeaderboard(leaderboardData)
      
      const hostRes = await fetch(`${API_BASE}/leaderboard?exclude_host=false`)
      if (hostRes.ok) {
        const allArticles = await hostRes.json()
        const hostOnly = allArticles.filter(a => a.author_name === 'Ben Fowler')
        setHostArticles(hostOnly)
      }
      
      const yourArticleData = leaderboardData.find(a => 
        a.title.includes(YOUR_ARTICLE_TITLE)
      )
      setYourArticle(yourArticleData)
      
      const statsRes = await fetch(`${API_BASE}/stats`)
      if (!statsRes.ok) throw new Error('Failed to fetch stats')
      const statsData = await statsRes.json()
      setStats(statsData)
      
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setDataLoading(false)
      setLoading(false)
    }
  }

  const getRank = (contentId) => {
    return leaderboard.findIndex(a => a.content_id === contentId) + 1
  }

  const checkCookieStatus = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${API_BASE}/cookies/status`)
      const data = await res.json()
      setCookieStatus(data)
      
      if (data.status !== 'valid') {
        setShowCookieModal(true)
        setLoading(false)
      }
    } catch (err) {
      console.error('Failed to check cookie status:', err)
      setCookieStatus({ status: 'error', message: 'Cannot connect to backend' })
      setShowCookieModal(true)
      setLoading(false)
    }
  }

  const handleCookieUpload = async (file) => {
    try {
      const text = await file.text()
      const cookies = JSON.parse(text)
      await uploadCookies(cookies)
    } catch (err) {
      alert('Invalid cookies.json file: ' + err.message)
    }
  }

  const handleCookiePaste = async () => {
    try {
      const cookies = JSON.parse(cookieText)
      await uploadCookies(cookies)
    } catch (err) {
      alert('Invalid JSON: ' + err.message)
    }
  }

  const uploadCookies = async (cookies) => {
    try {
      const res = await fetch(`${API_BASE}/cookies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookies })
      })
      const data = await res.json()
      
      if (data.status === 'success') {
        alert(data.message)
        setShowCookieModal(false)
        setCookieText('')
        await checkCookieStatus()
        fetchData()
      } else {
        alert('Error: ' + data.message)
      }
    } catch (err) {
      alert('Failed to upload cookies: ' + err.message)
    }
  }

  const sortedLeaderboard = [...leaderboard].sort((a, b) => {
    if (sortBy === 'likes_count') return b.likes_count - a.likes_count
    if (sortBy === 'comments_count') return b.comments_count - a.comments_count
    return b.engagement_score - a.engagement_score
  })

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  if (cookieStatus?.status !== 'valid' && !showCookieModal) {
    return (
      <div className="app">
        <div className="header">
          <h1>AIdeas 2025 Leaderboard</h1>
        </div>
        <div className="cookie-required">
          <p>Authentication required. Please upload AWS Builder session cookies.</p>
          <button onClick={() => setShowCookieModal(true)}>Upload Cookies</button>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="header">
        <h1>AIdeas 2025 Leaderboard</h1>
        <div className="header-actions">
          <button onClick={fetchData} disabled={dataLoading}>
            {dataLoading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button onClick={() => setShowCookieModal(true)}>Manage Cookies</button>
        </div>
      </div>

      {yourArticle && stats && (
        <div className="your-stats">
          <h2>Your Submission</h2>
          <div className="stats-row">
            <div className="stat">
              <span className="stat-label">Rank</span>
              <span className="stat-value">#{getRank(yourArticle.content_id)} / {stats.total_articles}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Likes</span>
              <span className="stat-value">{yourArticle.likes_count}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Comments</span>
              <span className="stat-value">{yourArticle.comments_count}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Score</span>
              <span className="stat-value">{yourArticle.engagement_score.toFixed(1)}</span>
            </div>
          </div>
          <div className="article-title">{yourArticle.title}</div>
          {yourArticle.article_url && (
            <a href={yourArticle.article_url} target="_blank" rel="noopener noreferrer">View Article →</a>
          )}
        </div>
      )}

      <div className="leaderboard-section">
        <div className="section-header">
          <h2>Competition Leaderboard ({leaderboard.length} submissions)</h2>
          {hostArticles.length > 0 && (
            <button className="link-btn" onClick={() => setShowHost(!showHost)}>
              {showHost ? 'Hide' : 'Show'} {hostArticles.length} host article{hostArticles.length > 1 ? 's' : ''}
            </button>
          )}
        </div>

        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="rank-col">Rank</th>
              <th className="title-col">Title</th>
              <th className="author-col">Author</th>
              <th className="num-col sortable" onClick={() => setSortBy('likes_count')}>
                Likes {sortBy === 'likes_count' && '↓'}
              </th>
              <th className="num-col sortable" onClick={() => setSortBy('comments_count')}>
                Comments {sortBy === 'comments_count' && '↓'}
              </th>
              <th className="num-col sortable" onClick={() => setSortBy('engagement_score')}>
                Score {sortBy === 'engagement_score' && '↓'}
              </th>
              <th className="action-col"></th>
            </tr>
          </thead>
          <tbody>
            {sortedLeaderboard.map((article, index) => {
              const isYours = article.content_id === yourArticle?.content_id
              return (
                <tr key={article.content_id} className={isYours ? 'highlight' : ''}>
                  <td className="rank-col">{index + 1}</td>
                  <td className="title-col">
                    {isYours && <span className="badge">YOU</span>}
                    {article.title}
                  </td>
                  <td className="author-col">{article.author_name || '—'}</td>
                  <td className="num-col">{article.likes_count}</td>
                  <td className="num-col">{article.comments_count}</td>
                  <td className="num-col">{article.engagement_score.toFixed(1)}</td>
                  <td className="action-col">
                    {article.article_url && (
                      <a href={article.article_url} target="_blank" rel="noopener noreferrer">View</a>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {showHost && hostArticles.length > 0 && (
          <div className="host-section">
            <h3>Host Articles (Not Ranked)</h3>
            <table className="leaderboard-table">
              <thead>
                <tr>
                  <th className="title-col">Title</th>
                  <th className="author-col">Author</th>
                  <th className="num-col">Likes</th>
                  <th className="num-col">Comments</th>
                  <th className="action-col"></th>
                </tr>
              </thead>
              <tbody>
                {hostArticles.map((article) => (
                  <tr key={article.content_id} className="host-row">
                    <td className="title-col">{article.title}</td>
                    <td className="author-col">{article.author_name}</td>
                    <td className="num-col">{article.likes_count}</td>
                    <td className="num-col">{article.comments_count}</td>
                    <td className="action-col">
                      {article.article_url && (
                        <a href={article.article_url} target="_blank" rel="noopener noreferrer">View</a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {stats && (
        <div className="footer-stats">
          Total: {stats.total_articles} articles • {stats.total_likes} likes • {stats.total_comments} comments
        </div>
      )}

      {showCookieModal && (
        <div className="modal-overlay" onClick={() => setShowCookieModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Manage Cookies</h2>
            <p>Export cookies from AWS Builder using EditThisCookie extension</p>
            
            <div className="form-section">
              <label>Upload cookies.json</label>
              <input 
                type="file" 
                accept=".json"
                onChange={(e) => e.target.files[0] && handleCookieUpload(e.target.files[0])}
              />
            </div>

            <div className="form-section">
              <label>Or paste JSON</label>
              <textarea
                value={cookieText}
                onChange={(e) => setCookieText(e.target.value)}
                placeholder='[{"name":"...","value":"...","domain":".aws.com"}]'
                rows={8}
              />
              <button onClick={handleCookiePaste}>Upload</button>
            </div>

            <button className="secondary" onClick={() => setShowCookieModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
