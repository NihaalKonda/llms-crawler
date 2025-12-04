# Automated `llms.txt` & `llms-full.txt` Generator

This project crawls a website, extracts its key public pages, and generates:

- `llms.txt` – a concise, spec-compliant index for LLMs
- `llms-full.txt` – a full markdown dump of the important page content

The system consists of:

- A **Python backend** that:
  - Crawls sites with a batched, multithreaded crawler
  - Handles retries with exponential backoff
  - Extracts metadata + main content
  - Generates `llms.txt` and `llms-full.txt`
  - **Automatic cache with 1-hour refresh** - updates content when sites change
  - Supports JavaScript-heavy sites with Playwright auto-detection
  - Exposes an HTTP API via FastAPI

- A **React frontend** that:
  - Lets users input a URL
  - Calls the backend API
  - Displays both `llms.txt` and `llms-full.txt`
  - Provides copy + download buttons

---

## Features

### Automatic Content Refresh
- **Smart change detection**: Monitors site structure and content for changes
- **Zero manual intervention**: Automatically checks for changes every 30 minutes when users request llms.txt
- **Efficient updates**: Only regenerates files when actual changes are detected
- **Dual hash system**:
  - Structure hash: Detects new/removed pages, navigation changes
  - Content hash: Detects updates to existing page content

### JavaScript Site Support
- **Auto-detection**: Automatically detects React, Vue, Angular, and Next.js sites
- **Playwright fallback**: Uses headless browser rendering when needed
- **Smart performance**: Only uses Playwright when necessary

### Content Filtering
- **llms.txt**: Concise navigation with home page content, skips deep subsections
- **llms-full.txt**: Comprehensive content for core pages only (depth < 2)
- **Optional section**: Deep nested links separated for reference

---

## Startup Instructions

### Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium  # For JavaScript site support
```

### Start Backend API
```bash
uvicorn backend.api_app:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

### POST /api/crawl
Crawl a website and generate llms.txt files (with automatic caching)

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "llms_txt": "...",
  "llms_full_txt": "...",
  "from_cache": true,
  "cached_at": "2025-12-04T10:30:00"
}
```

### GET /api/cache/status?url=https://example.com
Check cache status for a URL

**Response:**
```json
{
  "cached": true,
  "url": "https://example.com",
  "cached_at": "2025-12-04T10:30:00",
  "age_hours": 0.5,
  "is_expired": false,
  "page_count": 15
}
```

### POST /api/cache/invalidate
Manually invalidate cache for a URL (forces fresh crawl)

**Request:**
```json
{
  "url": "https://example.com"
}
```

---

## How It Works

### Automatic Refresh Flow
1. User requests llms.txt for a site
2. System checks cache:
   - **Recent check (< 30 minutes)**: Return cached data instantly
   - **Time to check (> 30 minutes)**: Crawl site and compare hashes
3. If changes detected:
   - Regenerate llms.txt and llms-full.txt
   - Update cache with new content
4. If no changes detected:
   - Keep existing files
   - Update last-checked timestamp

### Change Detection Strategy
- **Dual hash comparison**:
  - Structure hash: SHA256 of (URLs, sections, depths, optional flags)
  - Content hash: SHA256 of all page content hashes combined
- **Check interval**: 30 minutes between change checks
- **Storage**: Local filesystem in `./cache` directory
- **Thread-safe**: Multiple concurrent requests handled safely
- **Efficient**: Only regenerates when content actually changes