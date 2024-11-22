"""
This file provides functionality to preprocess videos by extracting metadata
and generating audio files. It includes functions to fetch video records from
a MongoDB database, extract video metadata, and generate audio files from videos.

Functions:
    step_10_00_preprocess_video(video_id: str, db: AsyncIOMotorDatabase) -> None:
        Preprocess a video by extracting metadata and generating an audio file.
    _extract_video_metadata(video_file: str) -> Dict[str, Optional[float]]:
        Extract basic metadata from the video file.
    _generate_audio_from_video(video_file: str, audio_path: Path) -> None:
        Generate audio from the given video file and save it.
"""
import os
from pathlib import Path
from typing import Dict, Optional

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase
from moviepy.editor import VideoFileClip

from ..common.decorators.step_tracker import track_step


@track_step
async def step_10_00_preprocess_video(video_id: str, db: AsyncIOMotorDatabase) -> None:
    """
    Preprocess a video by extracting metadata and generating audio file.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Raises:
        ValueError: If video record is not found or video processing fails
        RuntimeError: If any preprocessing step fails
    """
    try:
        # Load environment variables
        load_dotenv()

        # Fetch video record
        video_record = await db.videos.find_one({"_id": ObjectId(video_id)})
        if not video_record:
            raise ValueError(f"Video record not found for ID: {video_id}")

        video_file = video_record['files']['video_file']

        print("Starting video preprocessing...")

        # Extract video metadata
        video_metadata = _extract_video_metadata(video_file)

        # Setup audio file path
        base_dir = Path(os.getenv('BASE_DIR', ''))
        audio_dir = base_dir / "audio_files"
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / f"{video_id}_audio.mp3"

        # Generate audio file
        _generate_audio_from_video(video_file, audio_path)

        # Update database with metadata and audio file path
        await db.videos.update_one(
            {"_id": ObjectId(video_id)},
            {
                "$set": {
                    "metadata": video_metadata,
                    "files.audio_file": str(audio_path)
                }
            }
        )

        print("Video preprocessing completed successfully")

    except Exception as e:
        raise RuntimeError(f"Video preprocessing failed: {str(e)}") from e


def _extract_video_metadata(video_file: str) -> Dict[str, Optional[float]]:
    """Extract basic metadata from the video file."""
    try:
        with VideoFileClip(video_file) as video:
            return {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'audio_fps': video.audio.fps if video.audio else None,
                'audio_nchannels': video.audio.nchannels if video.audio else None
            }
    except Exception as e:
        raise ValueError(f"Failed to extract video metadata: {str(e)}") from e


def _generate_audio_from_video(video_file: str, audio_path: Path) -> None:
    """Generate audio from the given video file and save it."""
    try:
        with VideoFileClip(video_file) as video:
            if video.audio is None:
                raise ValueError("Video has no audio track")
            video.audio.write_audiofile(str(audio_path))
    except Exception as e:
        raise ValueError(f"Failed to generate audio: {str(e)}") from e
