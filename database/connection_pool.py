from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from settings.Settings import settings


def get_db_client():
    client = MongoClient(settings.database_url, maxPoolSize=50)
    return client


def get_db_client_async():
    client = AsyncIOMotorClient(settings.database_url, maxPoolSize=50)
    return client
