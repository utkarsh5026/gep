from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/llm")


class ContextFile(BaseModel):
    path: str
    startLine: int
    endLine: int


class ChatMessage(BaseModel):
    chatId: str
    message: str
    contextFiles: list[ContextFile]
    githubRepo: str


@router.post("/chat")
async def chat(message: ChatMessage):
    print(message)
    return {"message": message}
