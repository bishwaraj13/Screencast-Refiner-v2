"""
This file provides functionality to fetch transcriptions for audio files using Rev AI API.
It includes functions to submit audio files for transcription and retrieve the results.

Functions:
    step_20_00_fetch_transcription(video_id: str, db: AsyncIOMotorDatabase) -> None:
        Fetch transcription for a video's audio file using Rev AI service.
"""

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase


from ..common.decorators.step_tracker import track_step
from ..common.services.transcription_manager import _process_transcription

@track_step
async def step_20_00_fetch_transcription(video_id: str, db: AsyncIOMotorDatabase) -> None:
    """
    Fetch transcription for a video's audio file using Rev AI service.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Raises:
        ValueError: If audio file not found or Rev AI token is missing
        RuntimeError: If transcription process fails
    """
    try:
        # Load environment variables
        load_dotenv()

        # Fetch video record
        video_record = await db.videos.find_one({"_id": ObjectId(video_id)})
        if not video_record:
            raise ValueError(f"Video record not found for ID: {video_id}")

        audio_file = video_record.get('files', {}).get('audio_file')
        if not audio_file:
            raise ValueError(f"Audio file not found for video ID: {video_id}")

        # Initialize Rev AI client and submit job
        transcription_result = await _process_transcription(audio_file)

        # Update database with transcription
        await db.transcriptions.insert_one(
            {
                    "video_id": ObjectId(video_id),
                    "transcription": transcription_result
            }
        )

        print("Transcription process completed successfully")

    except Exception as e:
        raise RuntimeError(f"Transcription process failed: {str(e)}") from e
