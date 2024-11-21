from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from typing import Optional


class MongoDBManager:
    _instance: Optional['MongoDBManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    async def initialize(self):
        """Initialize MongoDB connection"""
        if self._client is None:
            load_dotenv()

            mongo_uri = os.getenv('MONGODB_URI')
            if not mongo_uri:
                raise ValueError(
                    "MongoDB URI not found in environment variables")

            try:
                self._client = AsyncIOMotorClient(mongo_uri,
                                                  tz_aware=True,
                                                  directConnection=True)

                self._db = self._client[os.getenv(
                    'MONGODB_DATABASE', 'proscreenerDev')]

                await self._client.admin.command('ping')
                print("Successfully connected to MongoDB")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
                raise

    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get MongoDB client"""
        if self._client is None:
            raise RuntimeError(
                "MongoDB client not initialized. Call initialize() first")
        return self._client

    @property
    def db(self):
        """Get default database"""
        if self._db is None:
            raise RuntimeError(
                "MongoDB database not initialized. Call initialize() first")
        return self._db
