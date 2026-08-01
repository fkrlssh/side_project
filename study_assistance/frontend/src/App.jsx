import { useState } from "react";
import { generateNote, generateQuiz, uploadDeck } from "./api";
import "./App.css";

const QUIZ_TYPES = [
  { value: "multiple_choice", label: "객관식" },
  { value: "short_answer", label: "주관식" },
  { value: "ox", label: "OX" },
];

const QUIZ_SOURCES = [
  { value: "study_note", label: "생성된 학습노트 기반" },
  { value: "original_ppt", label: "원본 PPT 기반" },
];

export default function App() {
  const [deck, setDeck] = useState(null);
  const [note, setNote] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [quizType, setQuizType] = useState("multiple_choice");
  const [quizSource, setQuizSource] = useState("study_note");
  const [questionCount, setQuestionCount] = useState(5);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    setError("");
    setDeck(null);
    setNote(null);
    setQuiz(null);
    setStatus("업로드 및 슬라이드 추출 중...");
    try {
      const result = await uploadDeck(file);
      setDeck(result);
      setStatus(`슬라이드 ${result.pages.length}장 추출 완료`);
    } catch (err) {
      setError(err.message);
      setStatus("");
    }
  }

  async function handleGenerateNote() {
    if (!deck) return;
    setError("");
    setStatus("학습노트 생성 중... (VLM 이미지 해석 포함, 시간이 걸릴 수 있습니다)");
    try {
      const result = await generateNote(deck.deck_id);
      setNote(result);
      setStatus("학습노트 생성 완료");
    } catch (err) {
      setError(err.message);
      setStatus("");
    }
  }

  async function handleGenerateQuiz() {
    if (!deck) return;
    setError("");
    setStatus("퀴즈 생성 중...");
    try {
      const result = await generateQuiz(deck.deck_id, quizSource, quizType, questionCount);
      setQuiz(result);
      setStatus("퀴즈 생성 완료");
    } catch (err) {
      setError(err.message);
      setStatus("");
    }
  }

  return (
    <div className="app">
      <h1>PPT 학습노트 도우미</h1>

      <section className="card">
        <h2>1. PPT 업로드</h2>
        <input type="file" accept=".pptx" onChange={handleFileChange} />
        {deck && <p>파일: {deck.filename} ({deck.pages.length} 슬라이드)</p>}
      </section>

      <section className="card">
        <h2>2. 학습노트 생성</h2>
        <button disabled={!deck} onClick={handleGenerateNote}>
          학습노트 생성
        </button>
        {note && <pre className="note">{note.markdown}</pre>}
      </section>

      <section className="card">
        <h2>3. 퀴즈 생성</h2>
        <label>
          유형:
          <select value={quizType} onChange={(e) => setQuizType(e.target.value)}>
            {QUIZ_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>
        <label>
          소스:
          <select value={quizSource} onChange={(e) => setQuizSource(e.target.value)}>
            {QUIZ_SOURCES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        <label>
          문항 수:
          <input
            type="number"
            min={1}
            max={20}
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
          />
        </label>
        <button disabled={!deck} onClick={handleGenerateQuiz}>
          퀴즈 생성
        </button>
        {quiz && (
          <ol className="quiz">
            {quiz.items.map((item, i) => (
              <li key={i}>
                <p>{item.question}</p>
                {item.choices && (
                  <ul>
                    {item.choices.map((c, j) => <li key={j}>{c}</li>)}
                  </ul>
                )}
                <p className="answer">정답: {item.answer}</p>
              </li>
            ))}
          </ol>
        )}
      </section>

      {status && <p className="status">{status}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
