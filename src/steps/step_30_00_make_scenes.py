"""
This file provides functionality to generate scene breakdowns from video transcriptions using Gemini AI.
It includes functions to process transcriptions and create structured scene data.

Functions:
    step_30_00_generate_scenes(video_id: str, db: AsyncIOMotorDatabase) -> str:
        Generate scene breakdowns from video transcription using Gemini AI service.
"""

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..common.utils.json_utils import load_json_from_string
from ..common.services.content_generation_manager import generate_content
from ..common.decorators.step_tracker import track_step
from ..common.static import prompt_template


@track_step
async def step_30_00_make_scenes(video_id: str, db: AsyncIOMotorDatabase) -> str:
    """
    Generate scene breakdowns from video transcription using Gemini AI service.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Returns:
        str: Video ID of the processed document

    Raises:
        ValueError: If transcription record not found or Gemini API key is missing
        RuntimeError: If scene generation process fails
    """
    try:
        # Load environment variables and configure Gemini
        load_dotenv()

        # Fetch transcription record
        transcription_record = await db.transcriptions.find_one(
            {"video_id": ObjectId(video_id)}
        )

        if not transcription_record:
            raise ValueError(f"Transcription record not found for video ID: {video_id}")

        # Prepare and send prompt to Content Generation Service
        print("[INFO] Preparing prompt for scene generation...")
        transcript_dict = str(transcription_record['transcription'])
        revised_prompt = prompt_template.replace('{transcription_dict}', transcript_dict)

        print("[INFO] Generating scenes...")
        response = generate_content(revised_prompt)

        print("[INFO] Scene generation completed successfully")
        scenes_data = load_json_from_string(response.text)

        # Process and store scene data
        for index, scene in enumerate(scenes_data['steps']):
            await db.scenes.insert_one({
                "video_id": ObjectId(video_id),
                "scene_index": index,
                "title": scene['title'],
                "time_start": scene['time_start'],
                "time_end": scene['time_end'],
                "original_narration": scene['original_narration'],
                "polished_narration": scene['polished_narration']
            })

    except Exception as e:
        raise RuntimeError(f"Scene generation process failed: {str(e)}") from e
