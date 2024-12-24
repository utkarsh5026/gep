import os


if __name__ == "__main__":
    import uvicorn

    if os.environ.get("ENV") == "prod":
        uvicorn.run(
            "web:fastapi_app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
    else:
        uvicorn.run(
            "web:fastapi_app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
