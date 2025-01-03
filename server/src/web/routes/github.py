from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from starlette.status import HTTP_404_NOT_FOUND

from github import git_manager
from logger import logger
from web.repo_llm import llm_manager

router = APIRouter(prefix="/github")


@router.get(
    "/check-git-url",
    summary="Check Git URL Validity",
    description="Validates if the provided URL points to an accessible GitHub repository",
    response_description="Returns 200 if repository is valid, 404 if not found or private",
    responses={
        200: {"description": "Repository is valid and accessible"},
        404: {"description": "Repository not found or is private"}
    }
)
async def check_git_url(
    url: str = Query(...,
                     description="The GitHub repository URL to validate",
                     example="https://github.com/username/repo"
                     )
):
    result = await git_manager.check_git_url(url)
    if result:
        logger.info(f"Git URL is valid: {url}")
        return Response(status_code=200)
    else:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Repository not found or private {url} {result}")


@router.get(
    "/download-github-repo",
    summary="Download GitHub Repository",
    description="Downloads the contents of a GitHub repository to the local system",
    response_model=dict,  # You might want to create a specific response model
    responses={
        200: {"description": "Repository successfully downloaded"},
        404: {"description": "Repository not found"},
        500: {"description": "Download failed"}
    }
)
async def download_github_repo(
    url: str = Query(...,
                     description="The GitHub repository URL to download",
                     example="https://github.com/username/repo"
                     )
):
    result = await git_manager.download_github_repo(url)
    return result


@router.get("/load-repo",
            summary="Load a github repository",
            description="Load a github repository")
async def load_repo(url: str):
    logger.info(f"Loading repository: {url}")
    result = await git_manager.load_repo(url)

    logger.info(f"Loaded repository: {url}")
    return result


@router.get("/file-content",
            summary="Get the content of a file",
            description="Get the content of a file")
async def get_file_content(repo_link: str, file_path: str):
    result = await llm_manager.get_file_content(repo_link, file_path)
    return result
