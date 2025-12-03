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
  - Exposes an HTTP API via FastAPI

- A **React frontend** that:
  - Lets users input a URL
  - Calls the backend API
  - Displays both `llms.txt` and `llms-full.txt`
  - Provides copy + download buttons

---

## Startup Instructions

Start backend API
 - uvicorn backend.api_app:app --reload --host 0.0.0.0 --port 8000

Start frontend
 - cd frontend
 - npm install
 - npm run dev