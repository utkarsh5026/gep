from fastapi import APIRouter

router = APIRouter(prefix="/settings")


@router.get("/")
async def get_settings(repo_link: str):
    return {"message": "Hello World"}


@router.get("/global")
async def get_global_settings():
    return {"message": "Hello World"}
