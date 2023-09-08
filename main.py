from logging.config import dictConfig
from fastapi.logger import logger
from starlette.middleware.cors import CORSMiddleware
from database.connection_pool import get_db_client, get_db_client_async
from logs.LogConfig import LogConfig
from fastapi import FastAPI
from routers import case_summary_router, background_tasks_router, meta
import logging

logger.setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(background_tasks_router.router)
app.include_router(case_summary_router.router)
app.include_router(meta.router)


@app.on_event("startup")
async def startup_event():  # pragma: no cover
    dictConfig(LogConfig().dict())
    app.state.mongodb = get_db_client_async()
    app.state.database = app.state.mongodb["generative_summarizer"]
    app.state.mongodbsync = get_db_client()
    app.state.databasesync = app.state.mongodbsync["generative_summarizer"]


@app.on_event("shutdown")
async def shutdown_event():  # pragma: no cover
    logger.info("Shutting down...")
    app.state.mongodb.close()
    app.state.mongodbsync.close()
    logger.info("Shutdown complete.")
