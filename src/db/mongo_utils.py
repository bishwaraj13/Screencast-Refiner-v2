from .mongo_client import MongoDBManager


async def get_mongodb():
    """Get MongoDB manager instance"""
    mongo_manager = MongoDBManager()
    if mongo_manager._client is None:
        await mongo_manager.initialize()
    return mongo_manager
