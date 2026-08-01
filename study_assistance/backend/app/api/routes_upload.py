import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import DeckExtractResponse
from app.services.deck_store import save_deck_pages
from app.services.ppt_extractor import extract_deck

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post("/upload", response_model=DeckExtractResponse)
async def upload_deck(file: UploadFile):
    if not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="only .pptx files are supported")

    deck_id = uuid.uuid4().hex[:12]
    deck_dir = settings.upload_dir / deck_id
    deck_dir.mkdir(parents=True, exist_ok=True)

    pptx_path = deck_dir / file.filename
    pptx_path.write_bytes(await file.read())

    pages = extract_deck(pptx_path, deck_id)
    save_deck_pages(deck_id, pages)

    return DeckExtractResponse(deck_id=deck_id, filename=file.filename, pages=pages)
