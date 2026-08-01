"""Generates quiz items from either the raw slide text or the generated study note.

Quiz type/source are request-time parameters (see QuizGenerateRequest), not
fixed at build time -- the caller picks per request.
"""

from app.models.schemas import QuizItem, QuizType

# TODO: replace with a real text-generation call (VLM in text-only mode, or a
# small text LLM) that produces `question_count` QuizItems of the requested
# QuizType from `source_text`.


def generate_quiz(source_text: str, quiz_type: QuizType, question_count: int) -> list[QuizItem]:
    raise NotImplementedError(
        "quiz generation model call not wired up yet - depends on VLM/text-LLM "
        "integration decided in vlm_client.py"
    )
