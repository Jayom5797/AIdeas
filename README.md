# AWS AIdeas 2025 Engagement Tracker

## Purpose
Read-only leaderboard tracking public engagement metrics (likes, comments) for AWS 10,000 AIdeas 2025 competition articles published on AWS Skill Builder.

## Data Source
- **Primary URL**: https://builder.aws.com/learn/topics/aideas-2025?tab=article
- **API Endpoint**: https://api.builder.aws.com/cs/content/tag?contentType=ARTICLE&tagName=aideas-2025
- **Data Type**: Publicly visible engagement metrics only
- **Method**: Direct HTTP requests to public API (no authentication required)

## Architecture

### Backend (Python + FastAPI)
- `scraper/`: Direct HTTP API client for AWS Skill Builder
- `api/`: FastAPI endpoints for leaderboard data
- `db/`: SQLite storage with historical snapshots

### Frontend (React + Vite)
- Sortable leaderboard table
- Engagement trend charts
- Configurable scoring models

### Scheduler
- Cron job for periodic data refresh (configurable interval)

## Ethical Considerations
- Read-only observation of public data
- Respects rate limits (configurable delays)
- No authentication bypass
- No automated engagement (no liking/commenting)
- User-agent identification
- Graceful failure on platform changes

## Known Limitations
- Dependent on AWS Skill Builder UI structure
- May break if platform changes significantly
- Engagement metrics don't predict judging outcomes
- Historical data only available from first scrape forward

## Setup
See `docs/SETUP.md` for installation and configuration.

## License
MIT - For competition intelligence purposes only.
