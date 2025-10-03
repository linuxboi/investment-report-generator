# Investment Report Generator Backend

Flask API that coordinates the multi-agent Gemini workflow, persists the
results, and serves the React dashboard for interactive analysis.

## Highlights

- **Team vs. Simple agents** – pick between the collaborative multi-agent
	pipeline or a lightweight single-agent flow for quick takes.
- **Persistent archive** – every run is stored in `backend/reports.db`
	alongside generated Markdown/PDF artefacts in `reports/output/`.
- **Retrieval-augmented chatbot** – conversational Q&A grounded in stored
	reports using Gemini text embeddings.
- **All-in-one UX** – the Flask app also serves the compiled React UI under the
	same origin for easy deployment.

## Prerequisites

- Python 3.11+ (tested with 3.13)
- Node.js 18+ (required once to build the frontend bundle)
- A Google Gemini API key exposed as `GOOGLE_API_KEY` (or any of the aliases in
	`config.py`)
- _(Optional)_ Tavily API key (`TAVILY_API_KEY`) for enhanced research steps

## Backend Environment Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file next to `config.py` and add your secrets:

```env
GOOGLE_API_KEY=your-key-here
# Optional, unlocks extended web research
TAVILY_API_KEY=your-tavily-key
```

The SQLite database (`reports.db`) is created automatically in the backend
folder. Remove the file to reset history.

## Building the Frontend

The React single-page app is compiled once and then served by Flask:

```powershell
cd ../frontend
npm install
npm run build
```

The build output lands in `frontend/dist/`, which `server.py` exposes under the
root route.

## Running the Flask Server

```powershell
cd ../backend
python server.py
```

Visit <http://localhost:5000> for the full dashboard.

### API at a Glance

- `POST /api/reports` – generate a report (`mode`: `team` or `simple`)
- `GET /api/reports` – list stored report metadata with summaries & downloads
- `GET /api/reports/<id>` – fetch a full Markdown payload for a specific report
- `POST /api/chat` – ask the chatbot questions grounded in stored content
- `GET /api/reports/files` – inspect the raw Markdown/PDF artefacts
- `GET /api/reports/files/<filename>` – download a specific artefact
- `GET /api/health` – lightweight readiness probe for monitoring

### Developer Experience Tips

- For rapid UI iteration, run Vite alongside Flask:

	```powershell
	cd frontend
	npm run dev
	```

	The dev server proxies `/api/*` calls to `http://localhost:5000`. Override the
	target by setting `VITE_API_URL` before launching Vite.

- The CLI entry points (`main.py` for multi-agent, `main_simple.py` for single
	agent) remain available and share the same environment configuration.

## Troubleshooting

- **Frontend showing 501 error** – build the SPA with `npm run build` so Flask
	can serve `frontend/dist/`.
- **Missing Gemini credentials** – ensure one of
	`google_api_key/GOOGLE_API_KEY/YOUR_GOOGLE_API_KEY` is present in the
	environment or `.env`.
- **Resetting storage** – delete `backend/reports.db` and the contents of
	`reports/output/` to clear history.
