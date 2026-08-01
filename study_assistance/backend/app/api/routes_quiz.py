from fastapi import APIRouter, HTTPException

from app.models.schemas import QuizGenerateRequest, QuizGenerateResponse, QuizSource
from app.services.deck_store import get_deck_pages
from app.services.quiz_generator import generate_quiz

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz_endpoint(req: QuizGenerateRequest):
    pages = get_deck_pages(req.deck_id)
    if pages is None:
        raise HTTPException(status_code=404, detail="deck not found - upload it first")

    if req.source == QuizSource.study_note:
        source_text = "\n\n".join(p.summary or p.raw_text for p in pages)
    else:
        source_text = "\n\n".join(p.raw_text for p in pages)

    items = generate_quiz(source_text, req.quiz_type, req.question_count)
    return QuizGenerateResponse(deck_id=req.deck_id, quiz_type=req.quiz_type, items=items)
