"""Centralized environment configuration utilities."""

from __future__ import annotations

import os
from typing import Iterable, Optional

from dotenv import load_dotenv

# Ensure .env values are available before lookups
load_dotenv()

_GOOGLE_KEY_CANDIDATES: tuple[str, ...] = (
    "google_api_key",
    "GOOGLE_API_KEY",
    "YOUR_GOOGLE_API_KEY",
)

_TAVILY_KEY_CANDIDATES: tuple[str, ...] = (
    "tavily_api_key",
    "TAVILY_API_KEY",
    "Tavily_api_key",
)


def _first_non_empty(names: Iterable[str]) -> Optional[str]:
    """Return the first environment variable that has a value."""

    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def get_google_api_key(*, required: bool = False) -> Optional[str]:
    """Fetch the Google API key, honoring multiple environment variable names."""

    key = _first_non_empty(_GOOGLE_KEY_CANDIDATES)
    if required and not key:
        raise EnvironmentError(
            "Missing Google API key. Set one of: google_api_key, GOOGLE_API_KEY, YOUR_GOOGLE_API_KEY."
        )
    return key


def get_tavily_api_key(*, required: bool = False) -> Optional[str]:
    """Fetch the Tavily API key, honoring multiple environment variable names."""

    key = _first_non_empty(_TAVILY_KEY_CANDIDATES)
    if required and not key:
        raise EnvironmentError(
            "Missing Tavily API key. Set one of: tavily_api_key, TAVILY_API_KEY, Tavily_api_key."
        )
    return key
