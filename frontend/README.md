# Investment Report Frontend

React + Tailwind dashboard that consumes the Flask investment analysis API.

## Quick Start

```powershell
cd frontend
npm install
```

### Development Mode

```powershell
npm run dev
```

The dev server runs on <http://localhost:5173>. API calls to `/api/*` are
proxied to `http://localhost:5000`, so make sure the Flask server is running.
Override the backend origin by setting `VITE_API_URL` before starting Vite.

### Production Build

```powershell
npm run build
```

The compiled assets appear in `frontend/dist/`. Serve them via Flask by running
`python backend/server.py`; static files are delivered automatically.

## Environment Variables

- `VITE_API_URL` (optional): Explicit backend base URL. Defaults to the
	Azure App Service endpoint in production builds and the same value during
	local development. Override this when running a local backend (e.g.
	`http://localhost:5000`) or when hosting the SPA on a different domain such
	as Vercel.

## Key Features

- Interactive form to trigger multi-agent (team) or single-agent analyses
- Live status updates and rich Markdown preview
- Download links for generated Markdown/PDF artefacts
- Saved artefacts list backed by the Flask `/api/reports` endpoint
- Embedded finance chatbot that cites report excerpts via `/api/chat`
