from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from web.routes import (
    github_router,
    llm_router,
    settings_router,
)

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_router)
app.include_router(llm_router)
app.include_router(settings_router)
