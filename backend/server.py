"""Flask application exposing the investment report generator with a web UI bridge."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from main import generate_investment_report_with_team
from main_simple import generate_investment_report_simple
from report_store import (
    get_report_record,
    init_db as init_report_store,
    list_report_records,
    save_report_record,
)
from chatbot import answer_question as chat_with_reports

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
REPORTS_DIR = PROJECT_ROOT / "reports" / "output"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIST),
    static_url_path="/assets",
)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
app.config["JSON_SORT_KEYS"] = False
app.logger.setLevel(logging.INFO)

init_report_store()


@app.errorhandler(BadRequest)
def handle_bad_request(exc: BadRequest):
    """Return JSON responses for validation errors."""

    return jsonify({"error": exc.description}), 400


@app.get("/api/health")
def healthcheck():
    """Cheap readiness probe for monitoring."""

    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})


def _build_downloads(markdown_path: Optional[str], pdf_path: Optional[str]) -> List[Dict[str, str]]:
    downloads: List[Dict[str, str]] = []
    for path_value, label in ((markdown_path, "Markdown"), (pdf_path, "PDF")):
        if not path_value:
            continue
        filename = Path(path_value).name
        downloads.append(
            {
                "label": label,
                "filename": filename,
                "url": f"/api/reports/files/{filename}",
            }
        )
    return downloads


def _serialize_report(record: Dict[str, Any], include_markdown: bool = False) -> Dict[str, Any]:
    payload = {
        "id": record["id"],
        "ticker": record["ticker"],
        "companyName": record.get("company_name"),
        "mode": record["mode"],
        "createdAt": record["created_at"],
        "summary": record.get("summary"),
        "preview": record.get("preview"),
        "markdownPath": record.get("markdown_path"),
        "pdfPath": record.get("pdf_path"),
    }

    if include_markdown:
        payload["reportMarkdown"] = record.get("report_markdown")

    payload["downloads"] = _build_downloads(record.get("markdown_path"), record.get("pdf_path"))
    return payload


@app.get("/api/reports")
def list_report_history():
    """Return stored report metadata."""

    records = list_report_records()
    items = [_serialize_report(record) for record in records]
    return jsonify({"items": items})


@app.get("/api/reports/files")
def list_report_files():
    """Return file-based artefacts from the output directory."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    items: List[Dict[str, Any]] = []

    for entry in sorted(REPORTS_DIR.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True):
        if not entry.is_file():
            continue

        suffix = entry.suffix.lower()
        if suffix not in {".md", ".pdf"}:
            continue

        stat = entry.stat()
        items.append(
            {
                "filename": entry.name,
                "type": "pdf" if suffix == ".pdf" else "markdown",
                "sizeBytes": stat.st_size,
                "modifiedAt": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "downloadUrl": f"/api/reports/files/{entry.name}",
            }
        )

    return jsonify({"items": items})


@app.get("/api/reports/files/<path:filename>")
def download_report_file(filename: str):
    """Serve generated reports from the output folder."""

    safe_path = (REPORTS_DIR / filename).resolve()
    if not safe_path.is_file() or REPORTS_DIR not in safe_path.parents:
        abort(404)

    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)


def _normalise_mode(raw_mode: str) -> str:
    candidate = raw_mode.strip().lower()
    if candidate in {"team", "multi", "advanced", "full"}:
        return "team"
    if candidate in {"simple", "single", "lite"}:
        return "simple"
    raise BadRequest("Mode must be 'team' or 'simple'.")


@app.post("/api/reports")
def create_report():
    """Generate a new investment report using the configured agents."""

    payload = request.get_json(silent=True) or {}
    ticker = str(payload.get("ticker", "")).strip()
    if not ticker:
        raise BadRequest("Ticker is required.")

    company_name = payload.get("companyName")
    if company_name is not None:
        company_name = str(company_name).strip() or None

    raw_mode = str(payload.get("mode", "team"))
    mode = _normalise_mode(raw_mode)
    save_to_file = bool(payload.get("saveToFile", True))

    normalised_ticker = ticker.upper()

    try:
        if mode == "team":
            result = generate_investment_report_with_team(
                ticker=normalised_ticker,
                company_name=company_name,
                save_to_file=save_to_file,
            )
            payload_out: Dict[str, Any] = {
                "ticker": result["ticker"],
                "companyName": result.get("company_name"),
                "timestamp": result["timestamp"],
                "mode": "team",
                "reportMarkdown": result["report_markdown"],
                "markdownPath": result.get("markdown_path"),
                "pdfPath": result.get("pdf_path"),
            }
        else:
            result = generate_investment_report_simple(
                ticker=normalised_ticker,
                company_name=company_name,
                save_to_file=save_to_file,
            )
            payload_out = {
                "ticker": result["ticker"],
                "companyName": result.get("company_name"),
                "timestamp": result["timestamp"],
                "mode": "simple",
                "reportMarkdown": result["analysis"],
                "markdownPath": result.get("markdown_path"),
                "pdfPath": result.get("pdf_path"),
            }
    except Exception as exc:  # pragma: no cover - defensive logging for runtime issues
        app.logger.exception("Failed to generate report for %s", normalised_ticker)
        return jsonify({"error": str(exc)}), 500

    if save_to_file:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    record = save_report_record(
        ticker=payload_out["ticker"],
        company_name=payload_out.get("companyName"),
        mode=payload_out["mode"],
        report_markdown=payload_out["reportMarkdown"],
        markdown_path=payload_out.get("markdownPath"),
        pdf_path=payload_out.get("pdfPath"),
    )

    serialized = _serialize_report(record, include_markdown=True)
    payload_out.update(
        {
            "reportId": serialized["id"],
            "createdAt": serialized["createdAt"],
            "summary": serialized.get("summary"),
            "preview": serialized.get("preview"),
            "downloads": serialized.get("downloads", []),
        }
    )

    app.logger.info(
        "Generated %s report for %s (company=%s, saved=%s)",
        mode,
        normalised_ticker,
        company_name or "N/A",
        save_to_file,
    )

    return jsonify(payload_out), 201


@app.get("/api/reports/<string:report_id>")
def get_report(report_id: str):
    """Fetch a specific stored report."""

    record = get_report_record(report_id)
    if not record:
        abort(404)

    return jsonify(_serialize_report(record, include_markdown=True))


@app.post("/api/chat")
def chat_with_report():
    """Conversational endpoint grounded in stored reports."""

    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        raise BadRequest("Message is required.")

    report_id = payload.get("reportId")
    if report_id is not None:
        report_id = str(report_id).strip() or None

    top_k = payload.get("topK", 5)
    try:
        top_k = max(1, min(int(top_k), 10))
    except (TypeError, ValueError):
        raise BadRequest("topK must be an integer between 1 and 10.")

    response = chat_with_reports(message, report_id=report_id, top_k=top_k)
    return jsonify(response)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    """Serve the compiled React application when available."""

    if path.startswith("api/"):
        abort(404)

    if not FRONTEND_DIST.exists():
        return (
            "Frontend build not found. Run 'npm install' and 'npm run build' in the frontend directory.",
            501,
        )

    candidate = FRONTEND_DIST / path
    if path and candidate.exists():
        return send_from_directory(FRONTEND_DIST, path)

    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
