# Investment Report Generator Backend

Flask API that orchestrates the multi-agent investment analysis workflow and
serves the React dashboard for interactive report generation.

## Prerequisites

- Python 3.11+ (tested with 3.13)
- Node.js 18+ (for the web UI build tooling)
- Google Gemini API key exposed as `GOOGLE_API_KEY` (or one of the aliases
	listed in `config.py`)

## Environment Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file next to `config.py` and add at least your Gemini key:

```env
GOOGLE_API_KEY=your-key-here
```

## Building the Frontend

Build the React single-page app once so that Flask can serve it:

```powershell
cd ../frontend
npm install
npm run build
```

The compiled assets land in `frontend/dist/`, which `backend/server.py` serves.

## Running the Flask Server

```powershell
cd ../backend
python server.py
```

The API and UI are now available at <http://localhost:5000>. Key endpoints:

- `POST /api/reports` — generate a new report (`mode` = `team` or `simple`)
- `GET /api/reports` — list stored report metadata (id, ticker, preview)
- `GET /api/reports/<id>` — fetch a specific report including full Markdown
- `POST /api/chat` — converse with the finance chatbot grounded in stored reports via Gemini embeddings
- `GET /api/reports/files` — raw filesystem listing (legacy / troubleshooting)
- `GET /api/reports/files/<filename>` — download generated files
- `GET /api/health` — lightweight readiness probe

### Developer Experience Shortcut

For hot-reload during UI work, run Vite in dev mode (port 5173) and start the
Flask server in another terminal. Set `VITE_API_URL=http://localhost:5000` when
launching `npm run dev`, or rely on the default proxy configuration in
`vite.config.js`.

## Batch & CLI Modes

The legacy terminal experiences remain available via `main.py` (multi-agent) and
`main_simple.py` (single-agent). They share logic with the Flask endpoints, so
environment setup is identical.
