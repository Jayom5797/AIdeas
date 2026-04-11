import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const isYourArticle = (title) =>
  title.includes('ASET') && title.toLowerCase().includes('academic safety')

function App() {
  const [finalsLeaderboard, setFinalsLeaderboard] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCookieModal, setShowCookieModal] = useState(false)
  const [cookieText, setCookieText] = useState('')
  const [cookieStatus, setCookieStatus] = useState(null)
  const [dataLoading, setDataLoading] = useState(false)
  const [sortBy, setSortBy] = useState('engagement_score')

  useEffect(() => { checkCookieStatus() }, [])

  useEffect(() => {
    if (cookieStatus?.status === 'valid') fetchData()
  }, [cookieStatus])

  const fetchData = async () => {
    try {
      setDataLoading(true)
      await fetch(`${API_BASE}/refresh`, { method: 'POST' })
      await new Promise(resolve => setTimeout(resolve, 2000))

      const [finalsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/leaderboard/finals?exclude_host=true`),
        fetch(`${API_BASE}/stats`),
      ])

      if (!finalsRes.ok) throw new Error('Failed to fetch finals leaderboard')
      if (!statsRes.ok) throw new Error('Failed to fetch stats')

      setFinalsLeaderboard(await finalsRes.json())
      setStats(await statsRes.json())
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setDataLoading(false)
      setLoading(false)
    }
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
      setCookieStatus({ status: 'error', message: 'Cannot connect to backend' })
      setShowCookieModal(true)
      setLoading(false)
    }
  }

  const handleCookieUpload = async (file) => {
    try {
      const cookies = JSON.parse(await file.text())
      await uploadCookies(cookies)
    } catch (err) {
      alert('Invalid cookies.json file: ' + err.message)
    }
  }

  const handleCookiePaste = async () => {
    try {
      await uploadCookies(JSON.parse(cookieText))
    } catch (err) {
      alert('Invalid JSON: ' + err.message)
    }
  }

  const uploadCookies = async (cookies) => {
    try {
      const res = await fetch(`${API_BASE}/cookies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cookies }),
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

  const sorted = [...finalsLeaderboard].sort((a, b) => {
    if (sortBy === 'likes_count') return b.likes_count - a.likes_count
    if (sortBy === 'comments_count') return b.comments_count - a.comments_count
    return b.engagement_score - a.engagement_score
  })

  const yourArticle = finalsLeaderboard.find(a => isYourArticle(a.title))
  const yourRank = sorted.findIndex(a => isYourArticle(a.title)) + 1

  if (loading) return <div className="app"><div className="loading">Loading...</div></div>

  if (cookieStatus?.status !== 'valid' && !showCookieModal) {
    return (
      <div className="app">
        <div className="header"><h1>AIdeas 2025 Finals</h1></div>
        <div className="cookie-required">
          <p>Authentication required. Please upload AWS Builder session cookies.</p>
          <button onClick={() => setShowCookieModal(true)}>Upload Cookies</button>
        </div>
      </div>
    )
  }

  if (error) return <div className="app"><div className="error"><strong>Error:</strong> {error}</div></div>

  return (
    <div className="app">
      <div className="header">
        <h1>🏆 AIdeas 2025 Finals</h1>
        <div className="header-actions">
          <button onClick={fetchData} disabled={dataLoading}>
            {dataLoading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button onClick={() => setShowCookieModal(true)}>Manage Cookies</button>
        </div>
      </div>

      <div className="finals-banner">
        Top 50 Finalists — Submission window Apr 4–17 • Voting Apr 17–24 • Winners announced Apr 30
      </div>

      {yourArticle && (
        <div className="your-stats">
          <h2>Your Submission <span className="badge finalist-badge">FINALIST</span></h2>
          <div className="stats-row">
            <div className="stat">
              <span className="stat-label">Rank</span>
              <span className="stat-value">#{yourRank} / {finalsLeaderboard.length}</span>
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
          <h2>Finals Leaderboard ({finalsLeaderboard.length} finalists)</h2>
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
            {sorted.map((article, index) => {
              const isYours = isYourArticle(article.title)
              return (
                <tr key={article.content_id} className={isYours ? 'highlight' : ''}>
                  <td className="rank-col" data-label="Rank">{index + 1}</td>
                  <td className="title-col" data-label="Title">
                    {isYours && <span className="badge">YOU</span>}
                    {article.title}
                  </td>
                  <td className="author-col" data-label="Author">{article.author_name || '—'}</td>
                  <td className="num-col" data-label="Likes">{article.likes_count}</td>
                  <td className="num-col" data-label="Comments">{article.comments_count}</td>
                  <td className="num-col" data-label="Score">{article.engagement_score.toFixed(1)}</td>
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
      </div>

      <div className="footer-stats">
        Finals: {finalsLeaderboard.length} finalists • {finalsLeaderboard.reduce((s, a) => s + a.likes_count, 0)} likes • {finalsLeaderboard.reduce((s, a) => s + a.comments_count, 0)} comments
      </div>

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
