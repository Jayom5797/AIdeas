# Project Structure

```
aideas-tracker/
├── backend/
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── fetcher.py           # HTTP client for AWS API
│   │   ├── parser.py             # Extract article data from JSON
│   │   └── config.py             # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI application
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models
│   │   └── operations.py         # Database operations
│   ├── requirements.txt
│   ├── main.py                   # Data collection entry point
│   └── test_api.py               # API endpoint verification
├── frontend/                     # (To be implemented)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Leaderboard.jsx
│   │   │   ├── ArticleRow.jsx
│   │   │   ├── TrendChart.jsx
│   │   │   └── Filters.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── README.md
└── SETUP.md
```

## Data Flow

1. **Fetcher** (HTTP) → Calls AWS Skill Builder API → Gets JSON response
2. **Parser** → Extracts engagement metrics → Validates data
3. **Database** → Stores articles + historical snapshots
4. **API** → Serves ranked data via FastAPI
5. **Frontend** → Displays leaderboard + charts (to be built)
