import asyncio
from src.db.mongo_utils import get_mongodb

from src.steps.step_10_00_preprocess_video import step_10_00_preprocess_video
from src.steps.step_20_00_transcribe_video import step_20_00_transcribe_video
from src.steps.step_30_00_make_scenes import step_30_00_make_scenes
from src.steps.step_40_00_extract_clips import step_40_00_extract_clips
from src.steps.step_50_00_generate_audio import step_50_00_generate_audio
from src.steps.step_60_00_add_voiceover import step_60_00_add_voiceover
from src.steps.step_70_00_assemble_video import step_70_00_assemble_video


async def process_submitted_video(video_id: str):
    # Initialize MongoDB connection
    mongodb = await get_mongodb()

    try:
        # Execute pipeline steps
        await step_10_00_preprocess_video(video_id=video_id, db=mongodb.db)
        await step_20_00_transcribe_video(video_id=video_id, db=mongodb.db)
        await step_30_00_make_scenes(video_id=video_id, db=mongodb.db)

        # Run steps 40 and 50 in parallel using asyncio.gather
        await asyncio.gather(
            step_40_00_extract_clips(video_id=video_id, db=mongodb.db),
            step_50_00_generate_audio(video_id=video_id, db=mongodb.db)
        )

        await step_60_00_add_voiceover(video_id=video_id, db=mongodb.db)
        await step_70_00_assemble_video(video_id=video_id, db=mongodb.db)
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
    finally:
        mongodb.client.close()

