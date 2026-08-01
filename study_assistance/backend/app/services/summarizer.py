"""Builds per-page summaries and a combined study note.

Page-to-page context is carried forward with an exponential decay, mirroring
an LSTM forget gate: the immediately preceding page contributes the most detail,
and contribution shrinks geometrically the further back a page is.
"""

from app.core.config import settings
from app.models.schemas import SlidePage
from app.services.vlm_client import get_vlm_client


def _weighted_context(pages: list[SlidePage], current_index: int) -> str:
    """Builds a decayed context string from up to `context_max_lookback` prior pages."""
    lines = []
    lookback = min(settings.context_max_lookback, current_index)
    for k in range(1, lookback + 1):
        prev = pages[current_index - k]
        weight = settings.context_decay_rate ** k
        if prev.summary is None:
            continue
        # Higher weight -> keep more of the summary; lower weight -> truncate harder.
        keep_chars = max(40, int(len(prev.summary) * weight))
        snippet = prev.summary[:keep_chars]
        lines.append(f"(page {prev.page_index}, weight={weight:.2f}) {snippet}")
    return "\n".join(reversed(lines))


def summarize_page(pages: list[SlidePage], page_index: int) -> str:
    """Fills in `pages[page_index].summary` and returns it."""
    page = pages[page_index]
    vlm = get_vlm_client()

    image_descriptions = []
    for image in page.images:
        if image.description is None:
            image.description = vlm.describe_image(image.file_path, page.raw_text)
        image_descriptions.append(image.description)

    prior_context = _weighted_context(pages, page_index)

    # TODO: swap this naive concatenation for an actual text-LLM call once one
    # is wired in (or reuse the VLM in text-only mode) to produce a real summary
    # instead of a structured concatenation.
    parts = []
    if prior_context:
        parts.append(f"[Context from previous pages]\n{prior_context}")
    parts.append(f"[Slide {page.page_index} text]\n{page.raw_text}")
    for i, desc in enumerate(image_descriptions):
        parts.append(f"[Image {i}]\n{desc}")

    summary = "\n\n".join(parts)
    page.summary = summary
    return summary


def build_study_note(pages: list[SlidePage]) -> str:
    for i in range(len(pages)):
        if pages[i].summary is None:
            summarize_page(pages, i)

    sections = [f"## Slide {p.page_index + 1}\n\n{p.summary}" for p in pages]
    return "\n\n".join(sections)
