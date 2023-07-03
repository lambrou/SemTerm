from logging.config import dictConfig

from pymongo import MongoClient

from logs.LogConfig import LogConfig
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routers import case_summary_router, background_tasks_router, meta
from settings.Settings import settings

app = FastAPI()

app.include_router(background_tasks_router.router)
app.include_router(case_summary_router.router)
app.include_router(meta.router)


@app.on_event("startup")
async def startup_event():
    dictConfig(LogConfig().dict())
    app.state.mongodb = AsyncIOMotorClient(settings.database_url)
    app.state.database = app.state.mongodb.generative_summarizer
    app.state.mongodbsync = MongoClient(settings.database_url)
    app.state.databasesync = app.state.mongodbsync['generative_summarizer']


@app.on_event("shutdown")
async def shutdown_event():
    app.state.mongodb.close()
    app.state.mongodbsync.close()
