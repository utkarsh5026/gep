import os
import uvicorn


def main():

    # Configure uvicorn loggers to use our logger
    # logging.getLogger("uvicorn").handlers = logger.handlers

    uvicorn_config = {
        "app": "web:fastapi_app",
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "reload": os.environ.get("ENV") != "prod",
        "log_config": None,
        # "access_log": True
    }

    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
