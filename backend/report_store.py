"""Persistent storage and retrieval helpers for generated reports."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from embeddings import embed_texts

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "reports.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    company_name TEXT,
    mode TEXT NOT NULL,
    created_at TEXT NOT NULL,
    summary TEXT,
    preview TEXT,
    report_markdown TEXT NOT NULL,
    markdown_path TEXT,
    pdf_path TEXT
);

CREATE TABLE IF NOT EXISTS report_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding TEXT NOT NULL,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_report_chunks_report_id ON report_chunks(report_id);
"""


def init_db() -> None:
    """Ensure the SQLite database and tables exist."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def _get_conn() -> Iterable[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _summarise_markdown(markdown: str) -> Dict[str, str]:
    text = markdown.strip()
    if not text:
        return {"summary": "", "preview": ""}

    summary = text.split("\n", 1)[0][:160]

    preview = text.replace("\n", " ")
    preview = " ".join(preview.split())
    preview = preview[:400] + ("…" if len(preview) > 400 else "")

    return {"summary": summary, "preview": preview}


def _chunk_markdown(markdown: str, max_chars: int = 1100, overlap: int = 150) -> List[str]:
    cleaned = [para.strip() for para in markdown.split("\n\n") if para.strip()]
    if not cleaned:
        return []

    chunks: List[str] = []
    buffer = ""

    for paragraph in cleaned:
        paragraph = paragraph.replace("\n", " ").strip()
        if not paragraph:
            continue

        if len(buffer) + len(paragraph) + 1 <= max_chars:
            buffer = f"{buffer} {paragraph}".strip()
            continue

        if buffer:
            chunks.append(buffer)
            tail = buffer[-overlap:].strip()
        else:
            tail = ""

        buffer = f"{tail} {paragraph}".strip()

    if buffer:
        chunks.append(buffer)

    return chunks


def save_report_record(
    *,
    ticker: str,
    company_name: Optional[str],
    mode: str,
    report_markdown: str,
    markdown_path: Optional[str],
    pdf_path: Optional[str],
) -> Dict[str, Optional[str]]:
    """Persist the generated report and its embeddings."""

    report_id = uuid.uuid4().hex
    created_at = datetime.utcnow().isoformat() + "Z"
    summary_info = _summarise_markdown(report_markdown)
    chunks = _chunk_markdown(report_markdown)

    chunk_embeddings: Optional[np.ndarray] = None
    if chunks:
        try:
            chunk_embeddings = embed_texts(chunks)
        except Exception:  # pragma: no cover - embedder failures should not abort storage
            chunk_embeddings = None

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO reports (
                id, ticker, company_name, mode, created_at,
                summary, preview, report_markdown, markdown_path, pdf_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                ticker,
                company_name,
                mode,
                created_at,
                summary_info["summary"],
                summary_info["preview"],
                report_markdown,
                markdown_path,
                pdf_path,
            ),
        )

        if chunk_embeddings is not None:
            for index, (chunk_text, embedding_vec) in enumerate(zip(chunks, chunk_embeddings), start=1):
                conn.execute(
                    """
                    INSERT INTO report_chunks (report_id, chunk_index, content, embedding)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        report_id,
                        index,
                        chunk_text,
                        json.dumps(embedding_vec.tolist()),
                    ),
                )

    return {
        "id": report_id,
        "ticker": ticker,
        "company_name": company_name,
        "mode": mode,
        "created_at": created_at,
        "summary": summary_info["summary"],
        "preview": summary_info["preview"],
        "report_markdown": report_markdown,
        "markdown_path": markdown_path,
        "pdf_path": pdf_path,
    }


def list_report_records() -> List[Dict[str, Optional[str]]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, ticker, company_name, mode, created_at, summary, preview, markdown_path, pdf_path
            FROM reports
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_report_record(report_id: str) -> Optional[Dict[str, Optional[str]]]:
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, ticker, company_name, mode, created_at, summary, preview,
                   report_markdown, markdown_path, pdf_path
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    return dict(row) if row else None


def search_report_chunks(
    query_embedding: np.ndarray,
    *,
    report_id: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Optional[str]]]:
    """Return the most similar report chunks for the given query embedding."""

    if query_embedding.ndim != 1:
        raise ValueError("query_embedding must be a 1D vector")

    with _get_conn() as conn:
        if report_id:
            rows = conn.execute(
                """
                SELECT report_id, chunk_index, content, embedding
                FROM report_chunks
                WHERE report_id = ?
                """,
                (report_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT report_id, chunk_index, content, embedding
                FROM report_chunks
                """
            ).fetchall()

    if not rows:
        return []

    scores: List[Dict[str, Optional[str]]] = []
    for row in rows:
        try:
            embedding = np.asarray(json.loads(row["embedding"]), dtype=np.float32)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        if embedding.shape != query_embedding.shape:
            continue
        score = float(np.dot(query_embedding, embedding))
        scores.append(
            {
                "report_id": row["report_id"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "score": score,
            }
        )

    scores.sort(key=lambda item: item["score"], reverse=True)
    return scores[:top_k]
