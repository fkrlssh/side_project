from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SlideImage(BaseModel):
    image_id: str
    file_path: str
    description: Optional[str] = None  # filled in by the VLM


class SlidePage(BaseModel):
    page_index: int
    raw_text: str
    images: list[SlideImage] = []
    summary: Optional[str] = None  # filled in by the summarizer


class DeckExtractResponse(BaseModel):
    deck_id: str
    filename: str
    pages: list[SlidePage]


class NoteGenerateRequest(BaseModel):
    deck_id: str


class NoteGenerateResponse(BaseModel):
    deck_id: str
    markdown: str


class QuizSource(str, Enum):
    original_ppt = "original_ppt"
    study_note = "study_note"


class QuizType(str, Enum):
    multiple_choice = "multiple_choice"
    short_answer = "short_answer"
    ox = "ox"


class QuizGenerateRequest(BaseModel):
    deck_id: str
    source: QuizSource = QuizSource.study_note
    quiz_type: QuizType = QuizType.multiple_choice
    question_count: int = 5


class QuizItem(BaseModel):
    question: str
    choices: Optional[list[str]] = None  # multiple_choice only
    answer: str
    explanation: Optional[str] = None


class QuizGenerateResponse(BaseModel):
    deck_id: str
    quiz_type: QuizType
    items: list[QuizItem]
