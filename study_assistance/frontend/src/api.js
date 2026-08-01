const API_BASE = "http://localhost:8000";

export async function uploadDeck(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/decks/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`upload failed: ${res.status}`);
  return res.json();
}

export async function generateNote(deckId) {
  const res = await fetch(`${API_BASE}/notes/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deck_id: deckId }),
  });
  if (!res.ok) throw new Error(`note generation failed: ${res.status}`);
  return res.json();
}

export async function generateQuiz(deckId, source, quizType, questionCount) {
  const res = await fetch(`${API_BASE}/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      deck_id: deckId,
      source,
      quiz_type: quizType,
      question_count: questionCount,
    }),
  });
  if (!res.ok) throw new Error(`quiz generation failed: ${res.status}`);
  return res.json();
}
