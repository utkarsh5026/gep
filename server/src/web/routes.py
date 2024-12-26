from github import git_config
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from starlette.status import HTTP_404_NOT_FOUND
from logger import logger


router = APIRouter(prefix="/github")


@router.get("/check-git-url",
            summary="Check if the git URL is valid",
            description="Check if the git URL is valid for a github repository")
async def check_git_url(url: str):
    result = await git_config.check_git_url(url)
    if result:
        logger.info(f"Git URL is valid: {url}")
        return Response(status_code=200)
    else:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Repository not found or private {url} {result}")


@router.get("/download-github-repo",
            summary="Download a github repository",
            description="Download a github repository")
async def download_github_repo(url: str):
    result = await git_config.download_github_repo(url)
    return result
