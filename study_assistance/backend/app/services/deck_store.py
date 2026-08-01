"""In-memory deck registry keyed by deck_id.

Good enough for a single-user local dev app. If this grows into something
multi-user/persistent, swap this for a real DB-backed store.
"""

from app.models.schemas import SlidePage

_decks: dict[str, list[SlidePage]] = {}


def save_deck_pages(deck_id: str, pages: list[SlidePage]) -> None:
    _decks[deck_id] = pages


def get_deck_pages(deck_id: str) -> list[SlidePage] | None:
    return _decks.get(deck_id)
