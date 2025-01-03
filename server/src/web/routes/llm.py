from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/llm")


class ContextFile(BaseModel):
    file_path: str
    start_line: int
    end_line: int


class ChatMessage(BaseModel):
    chat_id: str
    message: str
    context_files: list[ContextFile]
    github_repo: str


@router.post("/chat")
async def chat(message: ChatMessage):
    print(message)
    return {"message": message}
