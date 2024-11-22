"""
This file provides functionality to fetch transcriptions for audio files using Rev AI API.
It includes functions to submit audio files for transcription and retrieve the results.

Functions:
    step_20_00_fetch_transcription(video_id: str, db: AsyncIOMotorDatabase) -> None:
        Fetch transcription for a video's audio file using Rev AI service.
"""
import os
import asyncio

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase
from rev_ai import apiclient
from rev_ai.models import JobStatus

from ..common.decorators.step_tracker import track_step


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


async def _process_transcription(audio_file: str) -> dict:
    """
    Process audio file transcription using Rev AI service.

    Args:
        audio_file (str): Path to the audio file

    Returns:
        dict: Transcription result

    Raises:
        ValueError: If Rev AI token is missing or transcription fails
    """
    # Get Rev AI access token
    rev_access_token = os.getenv('REV_ACCESS_TOKEN')
    if not rev_access_token:
        raise ValueError("REV_ACCESS_TOKEN not found in environment variables")

    # Initialize Rev AI client
    client = apiclient.RevAiAPIClient(rev_access_token)

    try:
        print("Submitting audio file for transcription...")
        job = client.submit_job_local_file(audio_file)
        print(f"Transcription job submitted. Job ID: {job.id}")

        # Wait for job completion
        while True:
            job_details = client.get_job_details(job.id)
            print(f"Job status: {job_details.status}")
            
            if job_details.status == JobStatus.TRANSCRIBED:
                break
            elif job_details.status == JobStatus.FAILED:
                raise ValueError(f"Transcription job failed: {job_details.failure_detail}")
            
            await asyncio.sleep(10)  # Wait for 10 seconds before checking again

        print("Transcription completed. Fetching results...")
        transcript = client.get_transcript_json(job.id)
        
        return transcript

    except Exception as e:
        raise ValueError(f"Transcription processing failed: {str(e)}") from e
    