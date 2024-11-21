from ..common.decorators.step_tracker import track_step
from ..db.mongo_utils import get_mongodb
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase


@track_step
async def STEP_10_00_preprocess_video(video_id: str, db: AsyncIOMotorDatabase):
    print("Preprocessing video")
    await asyncio.sleep(5)
    print("Preprocessing complete")
