from fastapi import APIRouter, HTTPException

from app.models.schemas import NoteGenerateRequest, NoteGenerateResponse
from app.services.summarizer import build_study_note
from app.services.deck_store import get_deck_pages

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/generate", response_model=NoteGenerateResponse)
async def generate_note(req: NoteGenerateRequest):
    pages = get_deck_pages(req.deck_id)
    if pages is None:
        raise HTTPException(status_code=404, detail="deck not found - upload it first")

    markdown = build_study_note(pages)
    return NoteGenerateResponse(deck_id=req.deck_id, markdown=markdown)
