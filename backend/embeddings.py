"""Utilities for text embedding using Gemini."""

from __future__ import annotations

from typing import Iterable, List

import numpy as np
import google.generativeai as genai

from config import get_google_api_key

_EMBED_MODEL_NAME = "models/text-embedding-004"
_EPS = 1e-12
_configured = False


def _ensure_client() -> None:
    global _configured
    if not _configured:
        api_key = get_google_api_key(required=True)
        genai.configure(api_key=api_key)
        _configured = True


def _embed_single(text: str) -> List[float]:
    _ensure_client()
    response = genai.embed_content(
        model=_EMBED_MODEL_NAME,
        content=text,
    )

    if isinstance(response, dict) and "embedding" in response:
        return response["embedding"]

    raise RuntimeError("Gemini embedding response missing 'embedding' field")


def embed_texts(texts: Iterable[str]) -> np.ndarray:
    """Return L2-normalised embeddings for the given texts."""

    vectors: List[List[float]] = []
    for text in texts:
        clean_text = (text or "").strip()
        if not clean_text:
            clean_text = " "
        vectors.append(_embed_single(clean_text))

    array = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    norms = np.maximum(norms, _EPS)
    return array / norms


def embed_text(text: str) -> np.ndarray:
    """Convenience wrapper to embed a single piece of text."""

    return embed_texts([text])[0]
