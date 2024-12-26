import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    import uvicorn
    logger.info("Starting the FastAPI server...")

    uvicorn_config = {
        "app": "web:fastapi_app",
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "reload": os.environ.get("ENV") != "prod",
        "log_config": None
    }

    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
