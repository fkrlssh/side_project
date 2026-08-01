from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_notes, routes_quiz, routes_upload

app = FastAPI(title="Study Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_upload.router)
app.include_router(routes_notes.router)
app.include_router(routes_quiz.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
