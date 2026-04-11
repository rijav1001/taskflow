from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.boards import router as boards_router
from app.api.lists import router as lists_router
from app.api.cards import router as cards_router

app = FastAPI(title="TaskFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(boards_router)
app.include_router(lists_router)
app.include_router(cards_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}